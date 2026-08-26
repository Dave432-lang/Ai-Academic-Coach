from logging.config import fileConfig
import os
import sys
from sqlalchemy import (
    engine_from_config,
    pool,
    Table,
    MetaData,
    Column,
    String,
    PrimaryKeyConstraint,
    inspect,
    text,
)
import alembic.context as context
import alembic.ddl.impl as impl

# Override Alembic version_table_impl to ensure version_num column is VARCHAR(64) instead of default VARCHAR(32)
def custom_version_table_impl(self, *, version_table, version_table_schema, version_table_pk, **kw):
    vt = Table(
        version_table,
        MetaData(),
        Column("version_num", String(64), nullable=False),
        schema=version_table_schema,
    )
    if version_table_pk:
        vt.append_constraint(
            PrimaryKeyConstraint("version_num", name=f"{version_table}_pkc")
        )
    return vt

impl.DefaultImpl.version_table_impl = custom_version_table_impl

# Ensure backend root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.database.connection import Base

# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name:
    fileConfig(config.config_file_name)

# Set database URL dynamically from Pydantic application settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_column_size=64,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Auto-expand version_num column on legacy alembic_version tables if length < 64
        inspector = inspect(connection)
        if inspector.has_table("alembic_version"):
            for col in inspector.get_columns("alembic_version"):
                if col.get("name") == "version_num" and (getattr(col.get("type"), "length", 0) or 0) < 64:
                    connection.execute(text("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(64);"))
                    connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_column_size=64,
        )

        with context.begin_transaction():
            context.run_migrations()
        connection.commit()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
