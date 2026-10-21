FROM ghcr.io/astral-sh/uv:0.13.4 AS uv-bin
FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/apps/api/src \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN groupadd --system --gid 10001 companyos \
    && useradd --system --uid 10001 --gid companyos --create-home companyos
WORKDIR /app
COPY --from=uv-bin /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --python 3.13 --no-dev --no-install-project
COPY alembic.ini ./alembic.ini
COPY apps/api ./apps/api
USER 10001:10001
EXPOSE 8000
CMD ["uv", "run", "--locked", "--no-sync", "uvicorn", "company_os.main:app", "--host", "0.0.0.0", "--port", "8000"]
