def test_get_health_status(client):
    """
    Test GET /health returns HTTP 200 and {'status': 'ok'}.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_get_health_detailed(client):
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
