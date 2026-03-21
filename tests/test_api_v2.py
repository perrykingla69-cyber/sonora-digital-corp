from fastapi.testclient import TestClient

from apps.api.app.main import app, create_app
from apps.api.app.services.memory_service import get_memory_service
from packages.memory.mystic_memory import MemoryService


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


def test_v2_includes_nomina_y_contactos_routes():
    paths = {route.path for route in app.routes}
    assert "/empleados" in paths
    assert "/contactos" in paths
    assert "/nomina/calculos/{empleado_id}" in paths


def test_v2_includes_dashboard_leads_alertas_routes():
    paths = {route.path for route in app.routes}
    assert "/dashboard" in paths
    assert "/leads" in paths
    assert "/alertas/config" in paths


def test_v2_create_app_factory():
    created = create_app()
    paths = {route.path for route in created.routes}
    assert created.title == "Mystic API v2"
    assert "/dashboard" in paths
    assert "/alertas/config" in paths


def test_v2_memory_routes_and_ingest_search(tmp_path):
    memory_service = MemoryService(data_dir=tmp_path)
    app.dependency_overrides[get_memory_service] = lambda: memory_service
    client = TestClient(app)

    try:
        ingest = client.post(
            "/api/memory/ingest",
            json={"key": "doc-test", "text": "aceite industrial fourgea", "metadata": {"source": "test"}},
        )
        assert ingest.status_code == 200

        docs = client.get("/api/memory/documents")
        assert docs.status_code == 200
        assert docs.json()[0]["key"] == "doc-test"

        search = client.post("/api/rag/search", json={"query": "aceite", "limit": 5})
        assert search.status_code == 200
        assert any(item["key"] == "doc-test" for item in search.json())

        feedback = client.post("/api/feedback/memory", json={"key": "doc-test", "rating": 5, "comment": "útil"})
        assert feedback.status_code == 200
        assert feedback.json()["rating"] == 5

        feedback_list = client.get("/api/feedback/memory/doc-test")
        assert feedback_list.status_code == 200
        assert feedback_list.json()[0]["comment"] == "útil"
    finally:
        app.dependency_overrides.pop(get_memory_service, None)
