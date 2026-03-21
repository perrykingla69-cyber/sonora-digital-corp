from fastapi.testclient import TestClient

from apps.api.app.main import app, create_app


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


def test_v2_memory_routes_and_ingest_search():
    client = TestClient(app)
    ingest = client.post("/api/memory/ingest", json={"key": "doc-test", "text": "aceite industrial fourgea", "metadata": {"source": "test"}})
    assert ingest.status_code == 200
    search = client.post("/api/rag/search", json={"query": "aceite", "limit": 5})
    assert search.status_code == 200
    assert any(item["key"] == "doc-test" for item in search.json())
