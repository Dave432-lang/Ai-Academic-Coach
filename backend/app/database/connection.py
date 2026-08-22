from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import get_logger
from app.database.models.base import Base

logger = get_logger("database")

# Create SQLAlchemy 2.x Engine using connection string from settings
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.LOG_LEVEL.upper() == "DEBUG",
    connect_args={"connect_timeout": 2},
)

# Session factory for generating database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session lifecycle management.
    Yields a database session and ensures proper closure after request handling.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> dict:
    """
    Tests database connectivity and returns connection details / extension status.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            pgvector_installed = False
            try:
                ext_result = conn.execute(
                    text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
                ).scalar()
                pgvector_installed = bool(ext_result)
            except Exception:
                pgvector_installed = False

            return {
                "status": "connected" if result == 1 else "unexpected_response",
                "pgvector_extension": pgvector_installed,
            }
    except Exception as e:
        logger.warning(f"Database connection check failed: {str(e)}")
        return {
            "status": "disconnected",
            "error": str(e),
            "pgvector_extension": False,
        }
