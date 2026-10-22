from __future__ import annotations

from collections.abc import Iterator
from uuid import UUID

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from company_os.db.base import Base
from company_os.db.models.task import TaskAuditEventRecord, TaskRecord
from company_os.domain.task_state import ActorType, TaskStatus, can_transition_task
from company_os.services.task_lifecycle import (
    CompletionVerificationRequired,
    InvalidTaskTransition,
    StaleTaskVersion,
    TaskNotFound,
    create_task,
    transition_task,
)


@pytest.fixture()
def session_factory() -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def _create_task(factory: sessionmaker[Session]) -> UUID:
    with factory.begin() as session:
        task = create_task(
            session,
            objective="Research a specified technology niche",
            created_by="founder:test",
            input_payload={"niche": "developer tools"},
            acceptance_criteria=[{"id": "source-quality", "required": True}],
            request_id="request-001",
        )
        return task.id


def _transition(
    factory: sessionmaker[Session],
    task_id: UUID,
    target: TaskStatus,
    expected_version: int,
    *,
    reason: str = "test transition",
    verification_evidence: dict[str, object] | None = None,
) -> TaskRecord:
    with factory.begin() as session:
        return transition_task(
            session,
            task_id=task_id,
            target_status=target,
            actor_type=ActorType.SYSTEM,
            actor_id="test-runtime",
            reason=reason,
            expected_version=expected_version,
            verification_evidence=verification_evidence,
        )


def test_create_task_persists_queued_state_and_creation_audit(
    session_factory: sessionmaker[Session],
) -> None:
    task_id = _create_task(session_factory)

    with session_factory() as session:
        task = session.get(TaskRecord, task_id)
        events = session.scalars(
            select(TaskAuditEventRecord).where(TaskAuditEventRecord.task_id == task_id)
        ).all()

    assert task is not None
    assert task.status == TaskStatus.QUEUED.value
    assert task.version == 1
    assert task.input_payload == {"niche": "developer tools"}
    assert len(events) == 1
    assert events[0].action == "task.created"
    assert events[0].to_status == TaskStatus.QUEUED.value
    assert events[0].request_id == "request-001"


def test_legal_path_requires_verification_before_completion(
    session_factory: sessionmaker[Session],
) -> None:
    task_id = _create_task(session_factory)
    _transition(session_factory, task_id, TaskStatus.PLANNING, 1)
    _transition(session_factory, task_id, TaskStatus.READY, 2)
    _transition(session_factory, task_id, TaskStatus.RUNNING, 3)
    _transition(session_factory, task_id, TaskStatus.VERIFYING, 4)
    task = _transition(
        session_factory,
        task_id,
        TaskStatus.COMPLETED,
        5,
        verification_evidence={
            "passed": True,
            "checks": [{"id": "acceptance", "result": "passed"}],
            "evidence_ref": "artifact://tests/acceptance-001",
        },
    )

    with session_factory() as session:
        events = session.scalars(
            select(TaskAuditEventRecord)
            .where(TaskAuditEventRecord.task_id == task_id)
            .order_by(TaskAuditEventRecord.created_at, TaskAuditEventRecord.to_version)
        ).all()

    assert task.status == TaskStatus.COMPLETED.value
    assert task.version == 6
    assert task.completed_at is not None
    assert len(events) == 6
    assert (
        events[-1].event_data["verification"]["evidence_ref"]
        == "artifact://tests/acceptance-001"
    )


def test_invalid_transition_does_not_mutate_or_audit(
    session_factory: sessionmaker[Session],
) -> None:
    task_id = _create_task(session_factory)
    with pytest.raises(InvalidTaskTransition):
        _transition(session_factory, task_id, TaskStatus.COMPLETED, 1)

    with session_factory() as session:
        task = session.get(TaskRecord, task_id)
        events = session.scalars(
            select(TaskAuditEventRecord).where(TaskAuditEventRecord.task_id == task_id)
        ).all()

    assert task is not None and task.status == TaskStatus.QUEUED.value
    assert task.version == 1
    assert len(events) == 1


def test_completion_without_passing_checks_is_rejected(
    session_factory: sessionmaker[Session],
) -> None:
    task_id = _create_task(session_factory)
    _transition(session_factory, task_id, TaskStatus.PLANNING, 1)
    _transition(session_factory, task_id, TaskStatus.READY, 2)
    _transition(session_factory, task_id, TaskStatus.RUNNING, 3)
    _transition(session_factory, task_id, TaskStatus.VERIFYING, 4)

    with pytest.raises(CompletionVerificationRequired):
        _transition(
            session_factory,
            task_id,
            TaskStatus.COMPLETED,
            5,
            verification_evidence={"passed": False, "checks": [], "evidence_ref": ""},
        )

    with session_factory() as session:
        task = session.get(TaskRecord, task_id)
    assert task is not None and task.status == TaskStatus.VERIFYING.value
    assert task.version == 5


def test_stale_version_is_rejected(session_factory: sessionmaker[Session]) -> None:
    task_id = _create_task(session_factory)
    _transition(session_factory, task_id, TaskStatus.PLANNING, 1)

    with pytest.raises(StaleTaskVersion):
        _transition(session_factory, task_id, TaskStatus.READY, 1)


def test_terminal_state_cannot_be_reopened(session_factory: sessionmaker[Session]) -> None:
    task_id = _create_task(session_factory)
    _transition(session_factory, task_id, TaskStatus.PLANNING, 1)
    _transition(session_factory, task_id, TaskStatus.READY, 2)
    _transition(session_factory, task_id, TaskStatus.RUNNING, 3)
    _transition(session_factory, task_id, TaskStatus.VERIFYING, 4)
    _transition(
        session_factory,
        task_id,
        TaskStatus.COMPLETED,
        5,
        verification_evidence={
            "passed": True,
            "checks": [{"id": "check"}],
            "evidence_ref": "artifact://ok",
        },
    )

    with pytest.raises(InvalidTaskTransition):
        _transition(session_factory, task_id, TaskStatus.RUNNING, 6)


def test_unknown_external_outcome_cannot_jump_to_running(
    session_factory: sessionmaker[Session],
) -> None:
    task_id = _create_task(session_factory)
    _transition(session_factory, task_id, TaskStatus.READY, 1)
    _transition(session_factory, task_id, TaskStatus.RUNNING, 2)
    _transition(session_factory, task_id, TaskStatus.UNKNOWN_OUTCOME, 3)

    with pytest.raises(InvalidTaskTransition):
        _transition(session_factory, task_id, TaskStatus.RUNNING, 4)


def test_empty_reason_is_rejected(session_factory: sessionmaker[Session]) -> None:
    task_id = _create_task(session_factory)
    with pytest.raises(ValueError, match="reason must not be empty"):
        _transition(session_factory, task_id, TaskStatus.PLANNING, 1, reason="  ")


def test_missing_task_is_reported(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        with pytest.raises(TaskNotFound):
            transition_task(
                session,
                task_id=UUID("00000000-0000-0000-0000-000000000001"),
                target_status=TaskStatus.PLANNING,
                actor_type=ActorType.SYSTEM,
                actor_id="test-runtime",
                reason="missing task test",
                expected_version=1,
            )


def test_state_machine_marks_terminal_states_as_non_transitionable() -> None:
    for status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
        assert not can_transition_task(status, TaskStatus.RUNNING)


def test_task_and_creation_audit_roll_back_together(
    session_factory: sessionmaker[Session],
) -> None:
    task_id: UUID | None = None
    with pytest.raises(RuntimeError, match="simulate caller failure"):
        with session_factory.begin() as session:
            task = create_task(
                session,
                objective="This task should roll back",
                created_by="founder:test",
            )
            task_id = task.id
            raise RuntimeError("simulate caller failure")

    assert task_id is not None
    with session_factory() as session:
        task = session.get(TaskRecord, task_id)
        audit_count = len(
            session.scalars(
                select(TaskAuditEventRecord).where(TaskAuditEventRecord.task_id == task_id)
            ).all()
        )

    assert task is None
    assert audit_count == 0
