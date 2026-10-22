"""FastAPI dependency providers for Company OS."""

from __future__ import annotations

import logging
from collections.abc import Iterator

from fastapi import HTTPException, Request, status
from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger("company_os.api.db")


def get_db_session(request: Request) -> Iterator[Session]:
    """Provide a managed database session for a request.

    Fails closed with HTTP 503 if the database is not configured or unavailable,
    without leaking connection strings or credentials.
    """
    engine: Engine | None = getattr(request.app.state, "engine", None)
    if engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured",
        )

    session_factory: sessionmaker[Session] | None = getattr(
        request.app.state, "session_factory", None
    )
    if session_factory is None:
        session_factory = sessionmaker(bind=engine, expire_on_commit=False)
        request.app.state.session_factory = session_factory

    try:
        with session_factory() as session:
            yield session
    except SQLAlchemyError as exc:
        logger.warning(
            "Database error during request session (error_type=%s)",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is unavailable",
        ) from None
