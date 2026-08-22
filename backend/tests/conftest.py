import os
import pytest
from fastapi.testclient import TestClient

# Force ENVIRONMENT to testing for test execution
os.environ["ENVIRONMENT"] = "testing"
os.environ["LOG_LEVEL"] = "WARNING"

from app.main import app
from app.core.config import get_settings


@pytest.fixture(scope="session")
def test_app():
    """
    Fixture returning initialized FastAPI application.
    """
    return app


@pytest.fixture(scope="session")
def client(test_app):
    """
    Fixture returning FastAPI HTTP TestClient powered by HTTPX.
    """
    with TestClient(test_app) as c:
        yield c


@pytest.fixture(scope="session")
def settings():
    """
    Fixture returning cached application settings.
    """
    return get_settings()
