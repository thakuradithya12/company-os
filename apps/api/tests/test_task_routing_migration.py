from __future__ import annotations

from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from company_os.db.base import Base
from company_os.db.models.task import TaskRecord
from company_os.domain.task_state import TaskStatus


def test_task_record_routing_fields() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    task_id = uuid4()
    with Session(engine) as session:
        task = TaskRecord(
            id=task_id,
            objective="Perform website audit",
            created_by="founder:alice",
            status=TaskStatus.QUEUED.value,
            assigned_agent_id="AG-04",
            routing_decision={
                "status": "routed",
                "selected_agent_id": "AG-04",
                "matched_category": "website_audit",
                "confidence": 1.0,
                "reason": "Matched to AG-04",
            },
        )
        session.add(task)
        session.commit()

    with Session(engine) as session:
        loaded = session.scalar(select(TaskRecord).where(TaskRecord.id == task_id))
        assert loaded is not None
        assert loaded.assigned_agent_id == "AG-04"
        assert loaded.routing_decision is not None
        assert loaded.routing_decision["selected_agent_id"] == "AG-04"
        assert loaded.routing_decision["status"] == "routed"

    Base.metadata.drop_all(engine)
    engine.dispose()
