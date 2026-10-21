import pytest
from pydantic import ValidationError

from company_os.settings import Settings


def test_production_requires_secret_and_database() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, environment="production")


def test_production_rejects_short_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            environment="production",
            app_secret_key="too-short",
            database_url="postgresql+psycopg://user:pass@localhost:5432/company_os",
        )


def test_production_accepts_well_formed_minimum_configuration() -> None:
    settings = Settings(
        _env_file=None,
        environment="production",
        app_secret_key="s" * 40,
        database_url="postgresql+psycopg://user:pass@localhost:5432/company_os",
    )

    assert settings.environment == "production"
    assert settings.database_url is not None
    assert "s" * 40 not in str(settings)


def test_unsupported_database_driver_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, environment="test", database_url="mysql://user:pass@host/db")
