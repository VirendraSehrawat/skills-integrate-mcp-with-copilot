import os
import sys
from pathlib import Path

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add project root to path so src package can be imported from alembic commands
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models import SQLModel

# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# these values are the target metadata for 'autogenerate' support.
# Ensure your models are imported so the metadata is available.
target_metadata = SQLModel.metadata

# Ensure the SQLite data directory exists before Alembic connects.
data_dir = Path(__file__).resolve().parent.parent / "src" / "data"
data_dir.mkdir(parents=True, exist_ok=True)

# Override URL from config to keep local path consistent.
config.set_main_option("sqlalchemy.url", "sqlite:///src/data/activities.db")


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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
