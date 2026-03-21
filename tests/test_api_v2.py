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
    assert "/runtime/skills" in paths


def test_v2_create_app_factory():
    created = create_app()
    paths = {route.path for route in created.routes}
    assert created.title == "Mystic API v2"
    assert "/dashboard" in paths
    assert "/alertas/config" in paths
    assert "/runtime/sessions" in paths


def test_v2_runtime_endpoints():
    client = TestClient(app)

    skills = client.get("/runtime/skills")
    assert skills.status_code == 200
    names = {item["name"] for item in skills.json()}
    assert "shell" in names
    assert "filesystem" in names

    session = client.post("/runtime/sessions", json={"tenant_id": "tenant-a"})
    assert session.status_code == 200
    assert session.json()["tenant_id"] == "tenant-a"

    decision = client.post(
        "/runtime/authorize",
        json={
            "tenant_id": "tenant-a",
            "skill_name": "github.write",
            "allowed_skills": ["github.write"],
            "blocked_scopes": ["github:write"],
        },
    )
    assert decision.status_code == 200
    assert decision.json()["allowed"] is False


def test_v2_memory_routes_and_ingest_search(tmp_path):
    memory_service = MemoryService(data_dir=tmp_path)
    app.dependency_overrides[get_memory_service] = lambda: memory_service
    client = TestClient(app)

    try:
        ingest = client.post(
            "/api/memory/ingest",
            json={
                "key": "doc-test",
                "text": "manual interno de aceite industrial fourgea para mantenimiento preventivo",
                "tenant_id": "tenant-a",
                "kind": "faq",
                "metadata": {"source": "test"},
            },
        )
        assert ingest.status_code == 200
        assert ingest.json()["tenant_id"] == "tenant-a"
        assert ingest.json()["kind"] == "faq"

        client.post(
            "/api/memory/ingest",
            json={
                "key": "doc-otro",
                "text": "panel comercial crm",
                "tenant_id": "tenant-b",
                "kind": "playbook",
                "metadata": {"source": "manual"},
            },
        )

        doc = client.get("/api/memory/documents/doc-test")
        assert doc.status_code == 200
        assert doc.json()["metadata"]["source"] == "test"

        docs = client.get("/api/memory/documents", params={"tenant_id": "tenant-a", "kind": "faq"})
        assert docs.status_code == 200
        assert [item["key"] for item in docs.json()] == ["doc-test"]

        search = client.post(
            "/api/rag/search",
            json={"query": "aceite", "limit": 5, "tenant_id": "tenant-a", "kind": "faq", "source": "test"},
        )
        assert search.status_code == 200
        payload = search.json()
        assert [item["key"] for item in payload] == ["doc-test"]
        assert payload[0]["source"] == "test"
        assert payload[0]["retrieval_mode"] == "lexical"
        assert "aceite" in payload[0]["evidence_snippet"].lower()

        no_hits = client.post(
            "/api/rag/search",
            json={"query": "inexistente", "limit": 5, "tenant_id": "tenant-a", "kind": "faq", "source": "test"},
        )
        assert no_hits.status_code == 200
        assert no_hits.json() == []

        feedback = client.post("/api/feedback/memory", json={"key": "doc-test", "rating": 5, "comment": "útil"})
        assert feedback.status_code == 200
        assert feedback.json()["rating"] == 5

        feedback_list = client.get("/api/feedback/memory/doc-test")
        assert feedback_list.status_code == 200
        assert feedback_list.json()[0]["comment"] == "útil"

        stats = client.get("/api/memory/stats", params={"tenant_id": "tenant-a"})
        assert stats.status_code == 200
        assert stats.json()["documents"] == 1
        assert stats.json()["feedback_items"] == 1
        assert stats.json()["avg_feedback_rating"] == 5.0
        assert stats.json()["search_queries"] == 2
        assert stats.json()["searches_with_results"] == 1
        assert stats.json()["search_hit_rate"] == 0.5
        assert stats.json()["feedback_coverage"] == 1.0

        deleted = client.delete("/api/memory/documents/doc-test")
        assert deleted.status_code == 204

        missing = client.get("/api/memory/documents/doc-test")
        assert missing.status_code == 404
    finally:
        app.dependency_overrides.pop(get_memory_service, None)
