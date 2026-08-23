import os
import sys
from pathlib import Path
from typing import Generator
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path for IDEs and test runners
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Force ENVIRONMENT to testing for test execution
os.environ["ENVIRONMENT"] = "testing"
os.environ["LOG_LEVEL"] = "WARNING"

try:
    from app.main import app
    from app.core.config import get_settings, Settings
except ImportError:
    from backend.app.main import app  # type: ignore
    from backend.app.core.config import get_settings, Settings  # type: ignore


@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    """
    Fixture returning initialized FastAPI application.
    """
    return app


@pytest.fixture(scope="session")
def client(test_app: FastAPI) -> Generator[TestClient, None, None]:
    """
    Fixture returning FastAPI HTTP TestClient powered by HTTPX.
    """
    with TestClient(test_app) as c:
        yield c


@pytest.fixture(scope="session")
def settings() -> Settings:
    """
    Fixture returning cached application settings.
    """
    return get_settings()
