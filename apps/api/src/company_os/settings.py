"""Validated environment settings for the Company OS API."""

from __future__ import annotations

from typing import Literal

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    """Validated application settings; secrets are excluded from display output."""

    model_config = SettingsConfigDict(
        env_prefix="COMPANY_OS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Literal["development", "test", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    database_url: str | None = None
    app_secret_key: SecretStr | None = None

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None

        try:
            parsed = make_url(value)
        except Exception as exc:
            raise ValueError("COMPANY_OS_DATABASE_URL is not a valid SQLAlchemy URL") from exc

        supported_drivers = {"postgresql+psycopg", "sqlite+pysqlite"}
        if parsed.drivername not in supported_drivers:
            raise ValueError(
                "Database URL driver must be postgresql+psycopg (runtime) "
                "or sqlite+pysqlite (tests only)"
            )
        return value

    @model_validator(mode="after")
    def validate_environment_requirements(self) -> Settings:
        if self.environment in {"staging", "production"}:
            if self.app_secret_key is None:
                raise ValueError(
                    "COMPANY_OS_APP_SECRET_KEY is required outside development/test"
                )
            if len(self.app_secret_key.get_secret_value()) < 32:
                raise ValueError("COMPANY_OS_APP_SECRET_KEY must contain at least 32 characters")
            if self.database_url is None:
                raise ValueError("COMPANY_OS_DATABASE_URL is required outside development/test")
            if self.database_url.startswith("sqlite"):
                raise ValueError("SQLite is not permitted in staging/production")
        if (
            self.environment != "test"
            and self.database_url
            and self.database_url.startswith("sqlite")
        ):
            raise ValueError("SQLite is permitted only when COMPANY_OS_ENVIRONMENT=test")
        return self
