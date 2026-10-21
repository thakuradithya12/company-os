"""Minimal API foundation: liveness and dependency-aware readiness only."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from company_os.settings import Settings

logger = logging.getLogger("company_os.health")


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    settings: Settings = application.state.settings
    engine: Engine | None = None
    if settings.database_url:
        engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=300)
    application.state.engine = engine
    try:
        yield
    finally:
        if engine is not None:
            engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create an API app; injectable settings keep tests deterministic."""
    app_settings = settings or Settings()
    application = FastAPI(
        title="Company OS API",
        description="Company OS engineering foundation. Business agents are not enabled.",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.state.settings = app_settings
    application.state.engine = None

    @application.get("/health/live", tags=["health"])
    def liveness() -> dict[str, str]:
        """Confirm the process is responsive without requiring external services."""
        return {"status": "ok", "service": "company-os-api"}

    @application.get("/health/ready", tags=["health"], response_model=None)
    def readiness(request: Request) -> JSONResponse | dict[str, object]:
        """Confirm the configured database can answer a simple query."""
        engine: Engine | None = request.app.state.engine
        if engine is None:
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "checks": {"database": "not_configured"}},
            )

        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            # Do not return DSNs, credentials, server banners, or raw database errors to callers.
            logger.warning("Database readiness check failed (error_type=%s)", type(exc).__name__)
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "checks": {"database": "unavailable"}},
            )

        return {"status": "ready", "checks": {"database": "ok"}}

    return application


app = create_app()
