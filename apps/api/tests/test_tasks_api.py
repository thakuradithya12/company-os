from __future__ import annotations

import http.server
import threading
from collections.abc import Iterator
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from company_os.db.base import Base
from company_os.db.models.task import TaskAuditEventRecord, TaskRecord
from company_os.domain.task_state import ActorType, TaskStatus
from company_os.main import create_app
from company_os.settings import Settings


@pytest.fixture()
def db_engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def app_with_db(db_engine):
    app = create_app(
        Settings(
            _env_file=None,
            environment="test",
            database_url="sqlite+pysqlite:///:memory:",
        )
    )
    app.state.engine = db_engine
    app.state.session_factory = sessionmaker(bind=db_engine, expire_on_commit=False)
    return app


@pytest.fixture()
def client(app_with_db) -> Iterator[TestClient]:
    with TestClient(app_with_db) as test_client:
        yield test_client


def test_create_task_minimal_payload(client: TestClient) -> None:
    payload = {
        "objective": "Build automated revenue report",
        "created_by": "founder:alice",
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    UUID(data["id"])  # must be valid UUID
    assert data["objective"] == "Build automated revenue report"
    assert data["created_by"] == "founder:alice"
    assert data["status"] == TaskStatus.QUEUED.value
    assert data["priority"] == 100
    assert data["max_attempts"] == 3
    assert data["attempt_count"] == 0
    assert data["version"] == 1
    assert data["input_payload"] == {}
    assert data["acceptance_criteria"] == []
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_create_task_full_payload_and_persistence(
    client: TestClient, db_engine
) -> None:
    payload = {
        "objective": "Run security scan",
        "created_by": "service:scanner",
        "input_payload": {"target": "internal-api"},
        "acceptance_criteria": [{"id": "no-high-vulns", "required": True}],
        "priority": 50,
        "max_attempts": 5,
        "actor_type": "service",
        "request_id": "req-xyz-123",
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201

    data = response.json()
    task_id = UUID(data["id"])
    assert data["priority"] == 50
    assert data["max_attempts"] == 5
    assert data["input_payload"] == {"target": "internal-api"}
    assert data["acceptance_criteria"] == [{"id": "no-high-vulns", "required": True}]

    # Verify persistence and atomic audit event creation in a fresh session
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)
    with factory() as session:
        persisted_task = session.scalar(
            select(TaskRecord).where(TaskRecord.id == task_id)
        )
        assert persisted_task is not None
        assert persisted_task.objective == "Run security scan"
        assert persisted_task.created_by == "service:scanner"
        assert persisted_task.priority == 50
        assert persisted_task.status == TaskStatus.QUEUED.value
        assert persisted_task.version == 1

        audit_events = list(
            session.scalars(
                select(TaskAuditEventRecord)
                .where(TaskAuditEventRecord.task_id == task_id)
                .order_by(TaskAuditEventRecord.created_at)
            )
        )
        assert len(audit_events) == 1
        event = audit_events[0]
        assert event.action == "task.created"
        assert event.actor_type == ActorType.SERVICE.value
        assert event.actor_id == "service:scanner"
        assert event.from_status is None
        assert event.to_status == TaskStatus.QUEUED.value
        assert event.from_version is None
        assert event.to_version == 1
        assert event.request_id == "req-xyz-123"
        assert event.event_data == {"priority": 50, "max_attempts": 5}


def test_get_task_success(client: TestClient) -> None:
    create_response = client.post(
        "/tasks",
        json={"objective": "Inspect customer churn", "created_by": "founder:test"},
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == task_id
    assert get_response.json()["objective"] == "Inspect customer churn"


def test_get_task_not_found(client: TestClient) -> None:
    missing_id = uuid4()
    response = client.get(f"/tasks/{missing_id}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert str(missing_id) in data["detail"]


def test_get_task_invalid_uuid(client: TestClient) -> None:
    response = client.get("/tasks/not-a-valid-uuid")
    assert response.status_code == 422


@pytest.mark.parametrize(
    "invalid_payload,expected_loc",
    [
        ({"created_by": "founder:1"}, "objective"),
        ({"objective": "", "created_by": "founder:1"}, "objective"),
        ({"objective": "   ", "created_by": "founder:1"}, "objective"),
        ({"objective": "valid objective"}, "created_by"),
        ({"objective": "valid objective", "created_by": ""}, "created_by"),
        ({"objective": "valid objective", "created_by": "   "}, "created_by"),
        (
            {"objective": "valid", "created_by": "founder:1", "max_attempts": 0},
            "max_attempts",
        ),
        (
            {"objective": "valid", "created_by": "founder:1", "max_attempts": -1},
            "max_attempts",
        ),
        (
            {"objective": "valid", "created_by": "founder:1", "actor_type": "alien"},
            "actor_type",
        ),
    ],
)
def test_create_task_validation_errors(
    client: TestClient, invalid_payload: dict, expected_loc: str
) -> None:
    response = client.post("/tasks", json=invalid_payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    locs = [
        str(err.get("loc", []))
        for err in data["detail"]
        if isinstance(err, dict)
    ]
    assert any(expected_loc in loc for loc in locs)


def test_task_api_database_not_configured() -> None:
    app = create_app(Settings(_env_file=None, environment="test", database_url=None))
    with TestClient(app) as test_client:
        post_response = test_client.post(
            "/tasks",
            json={"objective": "Test without db", "created_by": "founder:1"},
        )
        assert post_response.status_code == 503
        assert post_response.json()["detail"] == "Database is not configured"

        get_response = test_client.get(f"/tasks/{uuid4()}")
        assert get_response.status_code == 503
        assert get_response.json()["detail"] == "Database is not configured"


def test_task_api_database_unavailable_does_not_leak_credentials() -> None:
    app = create_app(
        Settings(
            _env_file=None,
            environment="test",
            database_url="sqlite+pysqlite:///:memory:",
        )
    )

    class FailingSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def begin(self):
            raise OperationalError(
                "connection to secret_user:super_secret_password failed",
                params=None,
                orig=Exception("internal auth error"),
            )

    app.state.engine = create_engine(
        "sqlite+pysqlite:///:memory:", poolclass=StaticPool
    )
    app.state.session_factory = lambda: FailingSession()

    with TestClient(app) as test_client:
        response = test_client.post(
            "/tasks",
            json={"objective": "Test error handling", "created_by": "founder:1"},
        )
        assert response.status_code == 503
        body_text = response.text
        assert "super_secret_password" not in body_text
        assert "secret_user" not in body_text
        assert "Traceback" not in body_text
        assert response.json()["detail"] == "Database service is unavailable"


def test_api_v1_route_prefix_supported(client: TestClient) -> None:
    response = client.post(
        "/api/v1/tasks",
        json={"objective": "Task via v1 prefix", "created_by": "founder:1"},
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    get_response = client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == task_id


def test_security_limitation_caller_supplied_identity_recorded_as_metadata(
    client: TestClient,
) -> None:
    """Document and verify that created_by is caller-supplied metadata.

    It is NOT verified authentication.
    """
    arbitrary_caller_id = "unverified-agent-or-user-42"
    response = client.post(
        "/tasks",
        json={
            "objective": "Verify unauthenticated provenance",
            "created_by": arbitrary_caller_id,
        },
    )
    assert response.status_code == 201
    assert response.json()["created_by"] == arbitrary_caller_id


def test_route_task_api_endpoint(client: TestClient) -> None:
    create_res = client.post(
        "/tasks",
        json={
            "objective": "Perform market research on cloud infrastructure",
            "created_by": "founder:1",
        },
    )
    assert create_res.status_code == 201
    task_id = create_res.json()["id"]

    route_res = client.post(f"/tasks/{task_id}/route")
    assert route_res.status_code == 200
    route_data = route_res.json()
    assert route_data["task"]["assigned_agent_id"] == "AG-03"
    assert route_data["task"]["status"] == "ready"
    assert route_data["routing_decision"]["selected_agent_id"] == "AG-03"

    # Verify GET /tasks/{task_id} reflects routing fields
    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 200
    assert get_res.json()["assigned_agent_id"] == "AG-03"
    assert get_res.json()["routing_decision"] is not None


def test_route_task_api_unsupported_blocks_task(client: TestClient) -> None:
    create_res = client.post(
        "/tasks",
        json={
            "objective": "xyz nonsense task with no matching keywords",
            "created_by": "founder:1",
        },
    )
    assert create_res.status_code == 201
    task_id = create_res.json()["id"]

    route_res = client.post(f"/tasks/{task_id}/route")
    assert route_res.status_code == 200
    route_data = route_res.json()
    assert route_data["task"]["assigned_agent_id"] is None
    assert route_data["task"]["status"] == "blocked"
    assert route_data["task"]["last_error_code"] == "ROUTING_UNSUPPORTED"
    assert route_data["routing_decision"]["status"] == "unsupported"


def test_route_task_api_missing_task_returns_404(client: TestClient) -> None:
    res = client.post(f"/tasks/{uuid4()}/route")
    assert res.status_code == 404


def test_execute_task_endpoint_success(client: TestClient) -> None:
    class DocHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Financial Research Evidence Data")

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), DocHandler)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        # Create and route task to AG-03
        create_res = client.post(
            "/tasks",
            json={
                "objective": "Perform market research on cloud infrastructure",
                "created_by": "founder:1",
            },
        )
        assert create_res.status_code == 201
        task_id = create_res.json()["id"]

        route_res = client.post(f"/tasks/{task_id}/route")
        assert route_res.status_code == 200
        assert route_res.json()["task"]["assigned_agent_id"] == "AG-03"

        # Execute research tool
        exec_res = client.post(
            f"/tasks/{task_id}/execute",
            json={
                "tool_id": "research.source_verifier",
                "parameters": {
                    "url": f"http://127.0.0.1:{port}/evidence",
                    "expected_snippet": "Financial Research Evidence Data",
                    "allow_loopback_for_testing": True,
                },
            },
        )
        assert exec_res.status_code == 200
        exec_data = exec_res.json()
        assert exec_data["status"] == "completed"
        assert exec_data["evidence_reference"].startswith("evidence:research:sha256:")
        assert exec_data["output_payload"]["status_code"] == 200

        # Verify task is now completed
        get_res = client.get(f"/tasks/{task_id}")
        assert get_res.status_code == 200
        assert get_res.json()["status"] == "completed"
        assert get_res.json()["completed_at"] is not None

        # Verify execution history endpoint
        hist_res = client.get(f"/tasks/{task_id}/executions")
        assert hist_res.status_code == 200
        executions = hist_res.json()
        assert len(executions) == 1
        assert executions[0]["id"] == exec_data["id"]
        assert executions[0]["tool_id"] == "research.source_verifier"
    finally:
        server.shutdown()
        server.server_close()


def test_execute_task_endpoint_missing_task_404(client: TestClient) -> None:
    res = client.post(
        f"/tasks/{uuid4()}/execute",
        json={"tool_id": "research.source_verifier", "parameters": {"url": "https://example.com"}},
    )
    assert res.status_code == 404


def test_execute_task_endpoint_tool_not_found_404(client: TestClient) -> None:
    create_res = client.post(
        "/tasks",
        json={"objective": "Test objective", "created_by": "founder:1"},
    )
    task_id = create_res.json()["id"]
    res = client.post(
        f"/tasks/{task_id}/execute",
        json={"tool_id": "unknown.tool", "parameters": {}},
    )
    assert res.status_code == 404


def test_execute_task_endpoint_unauthorized_tool_403(
    client: TestClient, app_with_db: Any
) -> None:
    # Task assigned to AG-07 (builder)
    task_id = uuid4()
    with app_with_db.state.session_factory() as session:
        with session.begin():
            task = TaskRecord(
                id=task_id,
                objective="Build landing page",
                created_by="founder:1",
                status=TaskStatus.READY.value,
                assigned_agent_id="AG-07",
                version=2,
            )
            session.add(task)

    res = client.post(
        f"/tasks/{task_id}/execute",
        json={
            "tool_id": "research.source_verifier",
            "parameters": {"url": "https://example.com"},
        },
    )
    assert res.status_code == 403


def test_execute_task_endpoint_invalid_parameters_422(client: TestClient) -> None:
    create_res = client.post(
        "/tasks",
        json={"objective": "Perform market research on tech trends", "created_by": "founder:1"},
    )
    task_id = create_res.json()["id"]
    client.post(f"/tasks/{task_id}/route")

    res = client.post(
        f"/tasks/{task_id}/execute",
        json={
            "tool_id": "research.source_verifier",
            "parameters": {"url": ""},  # empty url rejected
        },
    )
    assert res.status_code == 422


def test_execute_task_endpoint_terminal_task_409(
    client: TestClient, app_with_db: Any
) -> None:
    task_id = uuid4()
    with app_with_db.state.session_factory() as session:
        with session.begin():
            task = TaskRecord(
                id=task_id,
                objective="Already completed task",
                created_by="founder:1",
                status=TaskStatus.COMPLETED.value,
                assigned_agent_id="AG-03",
                version=4,
            )
            session.add(task)

    res = client.post(
        f"/tasks/{task_id}/execute",
        json={
            "tool_id": "research.source_verifier",
            "parameters": {"url": "https://example.com"},
        },
    )
    assert res.status_code == 409


def test_get_task_executions_missing_task_404(client: TestClient) -> None:
    res = client.get(f"/tasks/{uuid4()}/executions")
    assert res.status_code == 404


