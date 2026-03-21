from fastapi.testclient import TestClient

from apps.api.app.main import app


def test_v2_root():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "MYSTIC API v2"


def test_v2_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "db" in data
