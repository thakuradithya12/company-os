from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from company_os.db.base import Base
from company_os.db.models.task import TaskAuditEventRecord, TaskRecord
from company_os.domain.agent_registry import (
    AgentAvailability,
    create_default_agent_registry,
)
from company_os.domain.task_router import (
    DeterministicTaskRouter,
    RoutingStatus,
)
from company_os.domain.task_state import ActorType, TaskStatus
from company_os.services.task_lifecycle import (
    InvalidTaskTransition,
    TaskNotFound,
    create_task,
)
from company_os.services.task_routing import route_task


@pytest.fixture()
def session_factory():
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


def test_route_task_success(session_factory) -> None:
    with session_factory.begin() as session:
        task = create_task(
            session,
            objective="Perform deep market research on enterprise observability",
            created_by="founder:test",
            request_id="req-1",
        )
        task_id = task.id

    with session_factory.begin() as session:
        routed_task, decision = route_task(
            session, task_id=task_id, request_id="req-route-1"
        )
        assert decision.status == RoutingStatus.ROUTED
        assert decision.selected_agent_id == "AG-03"
        assert routed_task.assigned_agent_id == "AG-03"
        assert routed_task.status == TaskStatus.READY.value
        assert routed_task.version == 2
        assert routed_task.routing_decision is not None
        assert routed_task.routing_decision["selected_agent_id"] == "AG-03"

    with session_factory() as session:
        persisted = session.scalar(select(TaskRecord).where(TaskRecord.id == task_id))
        assert persisted is not None
        assert persisted.assigned_agent_id == "AG-03"
        assert persisted.status == TaskStatus.READY.value

        events = list(
            session.scalars(
                select(TaskAuditEventRecord)
                .where(TaskAuditEventRecord.task_id == task_id)
                .order_by(TaskAuditEventRecord.created_at)
            )
        )
        assert len(events) == 2
        create_event, route_event = events
        assert create_event.action == "task.created"
        assert route_event.action == "task.routed"
        assert route_event.actor_type == ActorType.SYSTEM.value
        assert route_event.actor_id == "system:router"
        assert route_event.from_status == TaskStatus.QUEUED.value
        assert route_event.to_status == TaskStatus.READY.value
        assert route_event.from_version == 1
        assert route_event.to_version == 2
        assert route_event.request_id == "req-route-1"


def test_route_task_unsupported(session_factory) -> None:
    with session_factory.begin() as session:
        task = create_task(
            session,
            objective="xyz unknown 12345 arbitrary non-matching text",
            created_by="founder:test",
        )
        task_id = task.id

    with session_factory.begin() as session:
        routed_task, decision = route_task(session, task_id=task_id)
        assert decision.status == RoutingStatus.UNSUPPORTED
        assert decision.selected_agent_id is None
        assert routed_task.assigned_agent_id is None
        assert routed_task.status == TaskStatus.BLOCKED.value
        assert routed_task.last_error_code == "ROUTING_UNSUPPORTED"
        assert "does not match" in str(routed_task.last_error_message)

    with session_factory() as session:
        events = list(
            session.scalars(
                select(TaskAuditEventRecord)
                .where(TaskAuditEventRecord.task_id == task_id)
                .order_by(TaskAuditEventRecord.created_at)
            )
        )
        assert len(events) == 2
        route_event = events[1]
        assert route_event.action == "task.routing_failed"
        assert route_event.to_status == TaskStatus.BLOCKED.value


def test_route_task_ambiguous(session_factory) -> None:
    with session_factory.begin() as session:
        task = create_task(
            session,
            objective="build research",
            created_by="founder:test",
        )
        task_id = task.id

    with session_factory.begin() as session:
        routed_task, decision = route_task(session, task_id=task_id)
        assert decision.status == RoutingStatus.AMBIGUOUS
        assert decision.selected_agent_id is None
        assert routed_task.assigned_agent_id is None
        assert routed_task.status == TaskStatus.BLOCKED.value
        assert routed_task.last_error_code == "ROUTING_AMBIGUOUS"

    with session_factory() as session:
        events = list(
            session.scalars(
                select(TaskAuditEventRecord)
                .where(TaskAuditEventRecord.task_id == task_id)
                .order_by(TaskAuditEventRecord.created_at)
            )
        )
        assert events[1].action == "task.routing_failed"


def test_route_task_unavailable_agent(session_factory) -> None:
    registry = create_default_agent_registry()
    registry.set_availability("AG-04", AgentAvailability.UNAVAILABLE)
    router = DeterministicTaskRouter(registry)

    with session_factory.begin() as session:
        task = create_task(
            session,
            objective="Perform website audit on candidate business domain",
            created_by="founder:test",
        )
        task_id = task.id

    with session_factory.begin() as session:
        routed_task, decision = route_task(
            session, task_id=task_id, router=router
        )
        assert decision.status == RoutingStatus.AGENT_UNAVAILABLE
        assert decision.selected_agent_id is None
        assert routed_task.assigned_agent_id is None
        assert routed_task.status == TaskStatus.BLOCKED.value
        assert routed_task.last_error_code == "AGENT_UNAVAILABLE"

    with session_factory() as session:
        events = list(
            session.scalars(
                select(TaskAuditEventRecord)
                .where(TaskAuditEventRecord.task_id == task_id)
                .order_by(TaskAuditEventRecord.created_at)
            )
        )
        assert events[1].action == "task.routing_failed"


def test_route_missing_task_raises_not_found(session_factory) -> None:
    missing_id = uuid4()
    with session_factory.begin() as session:
        with pytest.raises(TaskNotFound):
            route_task(session, task_id=missing_id)


def test_route_terminal_task_rejected(session_factory) -> None:
    with session_factory.begin() as session:
        task = create_task(
            session,
            objective="Completed research task",
            created_by="founder:test",
        )
        task.status = TaskStatus.COMPLETED.value
        task_id = task.id

    with session_factory.begin() as session:
        with pytest.raises(InvalidTaskTransition):
            route_task(session, task_id=task_id)
