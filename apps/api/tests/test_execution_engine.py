from __future__ import annotations

import http.server
import threading
from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from company_os.db.base import Base
from company_os.db.models.task import (
    TaskAuditEventRecord,
    TaskExecutionRecord,
    TaskRecord,
)
from company_os.domain.task_state import TaskStatus
from company_os.domain.tools import ExecutionStatus
from company_os.services.execution_engine import (
    ConcurrentExecutionConflictError,
    TaskNotFound,
    TaskTerminalStateError,
    ToolNotFoundError,
    ToolValidationError,
    UnauthorizedToolError,
    execute_task_tool,
    mark_interrupted_executions,
)


class _LocalTestServer:
    def __init__(self, handler_cls: type[http.server.BaseHTTPRequestHandler]) -> None:
        self.server = http.server.HTTPServer(("127.0.0.1", 0), handler_cls)
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def db_session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_successful_execution_and_completion_gate(
    db_session_factory: sessionmaker[Session],
) -> None:
    class DocHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Q3 Financial Results 2026</h1></body></html>")

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = _LocalTestServer(DocHandler)
    try:
        task_id = uuid4()
        with db_session_factory() as session:
            with session.begin():
                task = TaskRecord(
                    id=task_id,
                    objective="Verify 2026 Q3 results source",
                    created_by="founder:alice",
                    status=TaskStatus.READY.value,
                    assigned_agent_id="AG-03",
                    version=2,
                )
                session.add(task)

        result = execute_task_tool(
            db_session_factory,
            task_id=task_id,
            tool_id="research.source_verifier",
            parameters={
                "url": f"http://127.0.0.1:{server.port}/q3",
                "expected_snippet": "Q3 Financial Results 2026",
                "allow_loopback_for_testing": True,
            },
        )

        assert result.status == ExecutionStatus.COMPLETED
        assert result.evidence_reference is not None
        assert result.evidence_reference.startswith("evidence:research:sha256:")
        assert result.error_message is None
        assert len(result.verification_checks) >= 3

        with db_session_factory() as session:
            task = session.scalar(select(TaskRecord).where(TaskRecord.id == task_id))
            assert task is not None
            assert task.status == TaskStatus.COMPLETED.value
            assert task.completed_at is not None

            executions = session.scalars(
                select(TaskExecutionRecord).where(TaskExecutionRecord.task_id == task_id)
            ).all()
            assert len(executions) == 1
            assert executions[0].status == ExecutionStatus.COMPLETED.value
            assert executions[0].evidence_reference == result.evidence_reference

            audit_events = session.scalars(
                select(TaskAuditEventRecord)
                .where(TaskAuditEventRecord.task_id == task_id)
                .order_by(TaskAuditEventRecord.created_at)
            ).all()
            actions = [e.action for e in audit_events]
            assert "execution.started" in actions
            assert "task.completed" in actions
    finally:
        server.stop()


def test_verification_failure_blocks_task(
    db_session_factory: sessionmaker[Session],
) -> None:
    class DocHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Wrong Content</h1></body></html>")

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = _LocalTestServer(DocHandler)
    try:
        task_id = uuid4()
        with db_session_factory() as session:
            with session.begin():
                task = TaskRecord(
                    id=task_id,
                    objective="Verify expected content",
                    created_by="founder:alice",
                    status=TaskStatus.READY.value,
                    assigned_agent_id="AG-03",
                    version=2,
                )
                session.add(task)

        result = execute_task_tool(
            db_session_factory,
            task_id=task_id,
            tool_id="research.source_verifier",
            parameters={
                "url": f"http://127.0.0.1:{server.port}/doc",
                "expected_snippet": "Missing Snippet",
                "allow_loopback_for_testing": True,
            },
        )

        assert result.status == ExecutionStatus.BLOCKED
        snippet_check = next(
            c for c in result.verification_checks if c["check_id"] == "snippet_present"
        )
        assert snippet_check["passed"] is False

        with db_session_factory() as session:
            task = session.scalar(select(TaskRecord).where(TaskRecord.id == task_id))
            assert task is not None
            assert task.status == TaskStatus.BLOCKED.value
            assert task.last_error_code == "EXECUTION_VERIFICATION_FAILED"
    finally:
        server.stop()


def test_ssrf_rejection_blocks_task(
    db_session_factory: sessionmaker[Session],
) -> None:
    task_id = uuid4()
    with db_session_factory() as session:
        with session.begin():
            task = TaskRecord(
                id=task_id,
                objective="Fetch internal metadata",
                created_by="founder:alice",
                status=TaskStatus.READY.value,
                assigned_agent_id="AG-03",
                version=2,
            )
            session.add(task)

    result = execute_task_tool(
        db_session_factory,
        task_id=task_id,
        tool_id="research.source_verifier",
        parameters={
            "url": "http://169.254.169.254/latest/meta-data/",
            "allow_loopback_for_testing": False,
        },
    )

    assert result.status == ExecutionStatus.FAILED
    assert result.error_message is not None
    assert "Prohibited IP" in result.error_message

    with db_session_factory() as session:
        task = session.scalar(select(TaskRecord).where(TaskRecord.id == task_id))
        assert task is not None
        assert task.status == TaskStatus.BLOCKED.value
        assert task.last_error_code == "EXECUTION_ERROR"


def test_unauthorized_tool_rejected(
    db_session_factory: sessionmaker[Session],
) -> None:
    task_id = uuid4()
    with db_session_factory() as session:
        with session.begin():
            task = TaskRecord(
                id=task_id,
                objective="Code generation task",
                created_by="founder:alice",
                status=TaskStatus.READY.value,
                assigned_agent_id="AG-07",  # Builder specialist
                version=2,
            )
            session.add(task)

    with pytest.raises(UnauthorizedToolError):
        execute_task_tool(
            db_session_factory,
            task_id=task_id,
            tool_id="research.source_verifier",
            parameters={"url": "https://example.com"},
        )


def test_unregistered_tool_rejected(
    db_session_factory: sessionmaker[Session],
) -> None:
    task_id = uuid4()
    with db_session_factory() as session:
        with session.begin():
            task = TaskRecord(
                id=task_id,
                objective="Generic task",
                created_by="founder:alice",
                status=TaskStatus.READY.value,
                assigned_agent_id="AG-03",
                version=2,
            )
            session.add(task)

    with pytest.raises(ToolNotFoundError):
        execute_task_tool(
            db_session_factory,
            task_id=task_id,
            tool_id="nonexistent.tool",
            parameters={},
        )


def test_invalid_parameters_rejected(
    db_session_factory: sessionmaker[Session],
) -> None:
    task_id = uuid4()
    with db_session_factory() as session:
        with session.begin():
            task = TaskRecord(
                id=task_id,
                objective="Research task",
                created_by="founder:alice",
                status=TaskStatus.READY.value,
                assigned_agent_id="AG-03",
                version=2,
            )
            session.add(task)

    with pytest.raises(ToolValidationError):
        execute_task_tool(
            db_session_factory,
            task_id=task_id,
            tool_id="research.source_verifier",
            parameters={"url": ""},  # empty URL forbidden
        )


def test_concurrent_execution_conflict(
    db_session_factory: sessionmaker[Session],
) -> None:
    task_id = uuid4()
    with db_session_factory() as session:
        with session.begin():
            task = TaskRecord(
                id=task_id,
                objective="Concurrent task",
                created_by="founder:alice",
                status=TaskStatus.RUNNING.value,
                assigned_agent_id="AG-03",
                version=3,
            )
            session.add(task)
            running_exec = TaskExecutionRecord(
                id=uuid4(),
                task_id=task_id,
                agent_id="AG-03",
                tool_id="research.source_verifier",
                risk_tier="tier_0_read_only",
                status=ExecutionStatus.RUNNING.value,
                input_parameters={"url": "https://example.com"},
                output_payload={},
                verification_checks=[],
            )
            session.add(running_exec)

    with pytest.raises(ConcurrentExecutionConflictError):
        execute_task_tool(
            db_session_factory,
            task_id=task_id,
            tool_id="research.source_verifier",
            parameters={"url": "https://example.com"},
        )


def test_terminal_task_execution_rejected(
    db_session_factory: sessionmaker[Session],
) -> None:
    task_id = uuid4()
    with db_session_factory() as session:
        with session.begin():
            task = TaskRecord(
                id=task_id,
                objective="Completed task",
                created_by="founder:alice",
                status=TaskStatus.COMPLETED.value,
                assigned_agent_id="AG-03",
                version=4,
            )
            session.add(task)

    with pytest.raises(TaskTerminalStateError):
        execute_task_tool(
            db_session_factory,
            task_id=task_id,
            tool_id="research.source_verifier",
            parameters={"url": "https://example.com"},
        )


def test_mark_interrupted_executions(
    db_session_factory: sessionmaker[Session],
) -> None:
    task_id = uuid4()
    exec_id = uuid4()
    with db_session_factory() as session:
        with session.begin():
            task = TaskRecord(
                id=task_id,
                objective="Crashed task",
                created_by="founder:alice",
                status=TaskStatus.RUNNING.value,
                assigned_agent_id="AG-03",
                version=3,
            )
            session.add(task)
            running_exec = TaskExecutionRecord(
                id=exec_id,
                task_id=task_id,
                agent_id="AG-03",
                tool_id="research.source_verifier",
                risk_tier="tier_0_read_only",
                status=ExecutionStatus.RUNNING.value,
                input_parameters={"url": "https://example.com"},
                output_payload={},
                verification_checks=[],
            )
            session.add(running_exec)

    with db_session_factory() as session:
        with session.begin():
            count = mark_interrupted_executions(session, task_id=task_id)
            assert count == 1

    with db_session_factory() as session:
        updated = session.scalar(
            select(TaskExecutionRecord).where(TaskExecutionRecord.id == exec_id)
        )
        assert updated is not None
        assert updated.status == ExecutionStatus.INTERRUPTED.value


def test_missing_task_raises_task_not_found(
    db_session_factory: sessionmaker[Session],
) -> None:
    with pytest.raises(TaskNotFound):
        execute_task_tool(
            db_session_factory,
            task_id=uuid4(),
            tool_id="research.source_verifier",
            parameters={"url": "https://example.com"},
        )
