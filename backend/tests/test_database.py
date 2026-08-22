from app.database.connection import engine, check_database_connection


def test_database_engine_configuration():
    """
    Test SQLAlchemy engine object creation and dialect configuration.
    """
    assert engine is not None
    assert engine.url is not None


def test_check_database_connection_structure():
    """
    Test check_database_connection helper function returns standard structure.
    """
    result = check_database_connection()
    assert isinstance(result, dict)
    assert "status" in result
    assert "pgvector_extension" in result
