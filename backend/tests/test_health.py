import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path for IDEs and test runners
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


def test_get_health_status(client: TestClient):
    """
    Test GET /health returns HTTP 200 and {'status': 'ok'}.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_get_health_detailed(client: TestClient):
    """
    Test GET /health?detailed=true includes app environment and database check response.
    """
    response = client.get("/health?detailed=true")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
    assert "version" in data
    assert "environment" in data
    assert "database" in data
