from fastapi.testclient import TestClient

from company_os.main import create_app
from company_os.settings import Settings


def test_liveness_does_not_depend_on_database() -> None:
    app = create_app(Settings(_env_file=None, environment="test", database_url=None))
    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "company-os-api"}


def test_readiness_fails_closed_when_database_is_not_configured() -> None:
    app = create_app(Settings(_env_file=None, environment="test", database_url=None))
    with TestClient(app) as client:
        response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "checks": {"database": "not_configured"},
    }


def test_readiness_checks_database_connectivity() -> None:
    app = create_app(
        Settings(
            _env_file=None,
            environment="test",
            database_url="sqlite+pysqlite:///:memory:",
        )
    )
    with TestClient(app) as client:
        response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "checks": {"database": "ok"}}
