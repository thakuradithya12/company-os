"""API foundation: health, readiness, and canonical task management."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from company_os.api.tasks import router as tasks_router
from company_os.settings import Settings

logger = logging.getLogger("company_os.api")


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    settings: Settings = application.state.settings
    engine: Engine | None = getattr(application.state, "engine", None)
    session_factory: sessionmaker[Session] | None = getattr(
        application.state, "session_factory", None
    )
    created_engine = False

    if engine is None and settings.database_url:
        engine_kwargs: dict[str, Any] = {"pool_pre_ping": True}
        if settings.database_url.startswith("sqlite"):
            engine_kwargs["poolclass"] = StaticPool
            engine_kwargs["connect_args"] = {"check_same_thread": False}
        else:
            engine_kwargs["pool_recycle"] = 300
        engine = create_engine(settings.database_url, **engine_kwargs)
        created_engine = True

    if session_factory is None and engine is not None:
        session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    application.state.engine = engine
    application.state.session_factory = session_factory
    try:
        yield
    finally:
        if created_engine and engine is not None:
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
    application.state.session_factory = None

    @application.exception_handler(SQLAlchemyError)
    def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.warning("Database error during request (error_type=%s)", type(exc).__name__)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database service is unavailable"},
        )

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

    application.include_router(tasks_router)
    application.include_router(tasks_router, prefix="/api/v1")

    return application


app = create_app()
