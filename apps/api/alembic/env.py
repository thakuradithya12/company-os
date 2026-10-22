from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import company_os.db.models  # noqa: F401  (register mapped tables on Base.metadata)
from company_os.db.base import Base
from company_os.settings import Settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = Settings()
if not settings.database_url:
    raise RuntimeError(
        "COMPANY_OS_DATABASE_URL is required to run migrations. "
        "Copy .env.example to .env and configure the local database."
    )
config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))

# Importing the models registers their tables on the shared metadata.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
