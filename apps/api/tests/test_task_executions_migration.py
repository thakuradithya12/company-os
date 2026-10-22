from __future__ import annotations

import importlib.util
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from company_os.db.base import Base
from company_os.db.models.task import TaskExecutionRecord, TaskRecord
from company_os.domain.task_state import TaskStatus
from company_os.domain.tools import ExecutionStatus, RiskTier


def test_task_execution_record_fields_and_relationship() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    task_id = uuid4()
    exec_id = uuid4()
    with Session(engine) as session:
        task = TaskRecord(
            id=task_id,
            objective="Verify financial reports source",
            created_by="founder:alice",
            status=TaskStatus.RUNNING.value,
            assigned_agent_id="AG-03",
        )
        session.add(task)
        session.flush()

        execution = TaskExecutionRecord(
            id=exec_id,
            task_id=task_id,
            agent_id="AG-03",
            tool_id="research.source_verifier",
            risk_tier=RiskTier.TIER_0_READ_ONLY.value,
            status=ExecutionStatus.COMPLETED.value,
            input_parameters={"url": "https://example.com/sec/10k"},
            output_payload={"status_code": 200, "content_sha256": "abc123hash"},
            evidence_reference="evidence:research:sha256:abc123hash",
            verification_checks=[
                {"check_id": "http_status", "passed": True, "details": "Status code 200"}
            ],
            duration_ms=120,
        )
        session.add(execution)
        session.commit()

    with Session(engine) as session:
        loaded_task = session.scalar(select(TaskRecord).where(TaskRecord.id == task_id))
        assert loaded_task is not None
        assert len(loaded_task.executions) == 1

        loaded_exec = loaded_task.executions[0]
        assert loaded_exec.id == exec_id
        assert loaded_exec.tool_id == "research.source_verifier"
        assert loaded_exec.risk_tier == RiskTier.TIER_0_READ_ONLY.value
        assert loaded_exec.status == ExecutionStatus.COMPLETED.value
        assert loaded_exec.evidence_reference == "evidence:research:sha256:abc123hash"
        assert loaded_exec.verification_checks[0]["check_id"] == "http_status"
        assert loaded_exec.duration_ms == 120
        assert loaded_exec.task.id == task_id

    Base.metadata.drop_all(engine)
    engine.dispose()


def test_migration_module_metadata() -> None:
    migration_path = Path(__file__).parents[1] / "alembic" / "versions" / "0004_task_executions.py"
    assert migration_path.exists()
    spec = importlib.util.spec_from_file_location("migration_0004", migration_path)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    assert migration.revision == "0004_task_executions"
    assert migration.down_revision == "0003_task_agent_routing"
    assert hasattr(migration, "upgrade")
    assert hasattr(migration, "downgrade")
