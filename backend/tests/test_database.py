import pytest
from sqlalchemy import text
from app.database.connection import engine, check_database_connection


def is_database_connected() -> bool:
    """Helper checking whether PostgreSQL is reachable for live integration tests."""
    status_info = check_database_connection()
    return status_info.get("status") == "connected"


def test_database_engine_configuration():
    """
    Test SQLAlchemy engine object creation and dialect configuration.
    """
    assert engine is not None
    assert engine.url is not None


def test_check_database_connection_structure():
    """
    Test check_database_connection helper function returns standard response format.
    """
    result = check_database_connection()
    assert isinstance(result, dict)
    assert "status" in result
    assert "pgvector_extension" in result


@pytest.mark.skipif(not is_database_connected(), reason="PostgreSQL database offline")
def test_live_database_connection_and_pgvector():
    """
    Integration Test: Test live database connection and pgvector extension verification.
    """
    result = check_database_connection()
    assert result["status"] == "connected"
    assert result["pgvector_extension"] is True


@pytest.mark.skipif(not is_database_connected(), reason="PostgreSQL database offline")
def test_live_alembic_migrations():
    """
    Integration Test: Verify live Alembic upgrade and schema tables.
    """
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    with engine.connect() as conn:
        tables = conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        ).scalars().all()
        assert "users" in tables
        assert "document_chunks" in tables


@pytest.mark.skipif(not is_database_connected(), reason="PostgreSQL database offline")
def test_live_updated_at_trigger():
    """
    Integration Test: Verify updated_at trigger updates timestamp on record modification.
    """
    from app.database.connection import SessionLocal
    from app.database.models import User, AccountStatus
    import time

    db = SessionLocal()
    try:
        user = User(email="trigger_test@example.com", password_hash="hash123", account_status=AccountStatus.ACTIVE)
        db.add(user)
        db.commit()
        db.refresh(user)

        initial_updated_at = user.updated_at
        time.sleep(0.1)

        user.password_hash = "new_hash456"
        db.commit()
        db.refresh(user)

        assert user.updated_at > initial_updated_at
    finally:
        db.delete(user)
        db.commit()
        db.close()
