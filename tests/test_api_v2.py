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
