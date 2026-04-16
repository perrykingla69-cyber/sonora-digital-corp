"""
Tests para endpoints de HERMES y MYSTIC.
Covers: /api/v1/agents/hermes/chat, /api/v1/agents/mystic/analyze
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from apps.api.main import app
from apps.api.app.core.database import get_tenant_session, Base


@pytest.fixture
def test_tenant_id():
    """UUID fijo para tests."""
    return uuid4()


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestHermesChatEndpoint:
    """Tests para POST /api/v1/agents/hermes/chat"""

    def test_hermes_chat_success(self, client, test_tenant_id):
        """Test exitoso — responde con estructura esperada."""
        response = client.post(
            "/api/v1/agents/hermes/chat",
            json={
                "tenant_id": str(test_tenant_id),
                "message": "¿Cuál es la tasa de IVA en México?",
                "context": None,
                "use_rag": True,
            },
        )
        assert response.status_code == 200
        data = response.json()

        assert "response" in data
        assert "sources" in data
        assert "confidence" in data
        assert "processing_time_ms" in data
        assert "used_mock" in data

        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
        assert isinstance(data["sources"], list)
        assert 0.0 <= data["confidence"] <= 1.0
        assert data["processing_time_ms"] >= 0
        assert isinstance(data["used_mock"], bool)

    def test_hermes_chat_with_context(self, client, test_tenant_id):
        """Test con contexto adicional."""
        response = client.post(
            "/api/v1/agents/hermes/chat",
            json={
                "tenant_id": str(test_tenant_id),
                "message": "¿Es deducible?",
                "context": "Tenemos gastos de transporte para clientes.",
                "use_rag": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["response"]) > 0

    def test_hermes_chat_missing_tenant_id(self, client):
        """Test fallo — falta tenant_id."""
        response = client.post(
            "/api/v1/agents/hermes/chat",
            json={
                "message": "Pregunta",
            },
        )
        assert response.status_code == 422  # Validation error

    def test_hermes_chat_missing_message(self, client, test_tenant_id):
        """Test fallo — falta message."""
        response = client.post(
            "/api/v1/agents/hermes/chat",
            json={
                "tenant_id": str(test_tenant_id),
            },
        )
        assert response.status_code == 422

    def test_hermes_chat_empty_message(self, client, test_tenant_id):
        """Test fallo — message vacío."""
        response = client.post(
            "/api/v1/agents/hermes/chat",
            json={
                "tenant_id": str(test_tenant_id),
                "message": "",
            },
        )
        assert response.status_code == 422

    def test_hermes_chat_long_message(self, client, test_tenant_id):
        """Test — message largo (pero dentro del límite)."""
        long_msg = "A" * 5000
        response = client.post(
            "/api/v1/agents/hermes/chat",
            json={
                "tenant_id": str(test_tenant_id),
                "message": long_msg,
            },
        )
        assert response.status_code == 200

    def test_hermes_chat_exceeds_max_length(self, client, test_tenant_id):
        """Test fallo — message excede límite."""
        long_msg = "A" * 5001
        response = client.post(
            "/api/v1/agents/hermes/chat",
            json={
                "tenant_id": str(test_tenant_id),
                "message": long_msg,
            },
        )
        assert response.status_code == 422

    def test_hermes_chat_use_rag_true(self, client, test_tenant_id):
        """Test con use_rag=true."""
        response = client.post(
            "/api/v1/agents/hermes/chat",
            json={
                "tenant_id": str(test_tenant_id),
                "message": "Pregunta con RAG",
                "use_rag": True,
            },
        )
        assert response.status_code == 200

    def test_hermes_chat_use_rag_false(self, client, test_tenant_id):
        """Test con use_rag=false (sin búsqueda)."""
        response = client.post(
            "/api/v1/agents/hermes/chat",
            json={
                "tenant_id": str(test_tenant_id),
                "message": "Pregunta sin RAG",
                "use_rag": False,
            },
        )
        assert response.status_code == 200


class TestMysticAnalyzeEndpoint:
    """Tests para GET /api/v1/agents/mystic/analyze"""

    def test_mystic_analyze_fiscal(self, client, test_tenant_id):
        """Test análisis fiscal."""
        response = client.get(
            "/api/v1/agents/mystic/analyze",
            params={
                "tenant_id": str(test_tenant_id),
                "analysis_type": "fiscal",
            },
        )
        assert response.status_code == 200
        data = response.json()

        assert "analysis" in data
        assert "alerts" in data
        assert "recommendations" in data
        assert "generated_at" in data
        assert "used_mock" in data

        assert isinstance(data["analysis"], str)
        assert len(data["analysis"]) > 0
        assert isinstance(data["alerts"], list)
        assert isinstance(data["recommendations"], list)

    def test_mystic_analyze_food(self, client, test_tenant_id):
        """Test análisis food/restaurante."""
        response = client.get(
            "/api/v1/agents/mystic/analyze",
            params={
                "tenant_id": str(test_tenant_id),
                "analysis_type": "food",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["analysis"]) > 0

    def test_mystic_analyze_business(self, client, test_tenant_id):
        """Test análisis business/general."""
        response = client.get(
            "/api/v1/agents/mystic/analyze",
            params={
                "tenant_id": str(test_tenant_id),
                "analysis_type": "business",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["analysis"]) > 0

    def test_mystic_analyze_alerts_structure(self, client, test_tenant_id):
        """Test estructura de alertas."""
        response = client.get(
            "/api/v1/agents/mystic/analyze",
            params={
                "tenant_id": str(test_tenant_id),
                "analysis_type": "fiscal",
            },
        )
        assert response.status_code == 200
        data = response.json()

        for alert in data["alerts"]:
            assert "level" in alert
            assert alert["level"] in ("critical", "warning", "info")
            assert "message" in alert
            assert isinstance(alert["message"], str)
            if "code" in alert:
                assert isinstance(alert["code"], str)

    def test_mystic_analyze_missing_tenant_id(self, client):
        """Test fallo — falta tenant_id."""
        response = client.get(
            "/api/v1/agents/mystic/analyze",
            params={
                "analysis_type": "fiscal",
            },
        )
        assert response.status_code == 422

    def test_mystic_analyze_missing_type(self, client, test_tenant_id):
        """Test fallo — falta analysis_type."""
        response = client.get(
            "/api/v1/agents/mystic/analyze",
            params={
                "tenant_id": str(test_tenant_id),
            },
        )
        assert response.status_code == 422

    def test_mystic_analyze_invalid_type(self, client, test_tenant_id):
        """Test fallo — tipo inválido."""
        response = client.get(
            "/api/v1/agents/mystic/analyze",
            params={
                "tenant_id": str(test_tenant_id),
                "analysis_type": "invalid",
            },
        )
        assert response.status_code == 422

    def test_mystic_analyze_cache(self, client, test_tenant_id):
        """Test cacheo — segunda llamada debe ser más rápida."""
        # Primera llamada
        r1 = client.get(
            "/api/v1/agents/mystic/analyze",
            params={
                "tenant_id": str(test_tenant_id),
                "analysis_type": "fiscal",
            },
        )
        assert r1.status_code == 200

        # Segunda llamada (debe estar en cache)
        r2 = client.get(
            "/api/v1/agents/mystic/analyze",
            params={
                "tenant_id": str(test_tenant_id),
                "analysis_type": "fiscal",
            },
        )
        assert r2.status_code == 200
        # Las dos respuestas deben ser idénticas
        assert r1.json()["analysis"] == r2.json()["analysis"]


class TestAgentsStatusEndpoint:
    """Tests para GET /api/v1/agents/status"""

    def test_agents_status(self, client, test_tenant_id):
        """Test status endpoint."""
        response = client.get(
            "/api/v1/agents/status",
            params={"tenant_id": str(test_tenant_id)},
        )
        assert response.status_code == 200
        data = response.json()

        assert "hermes" in data
        assert "mystic" in data
        assert "rag" in data
        assert "tenant_id" in data

        assert data["hermes"]["status"] == "active"
        assert data["mystic"]["status"] == "active"
        assert data["rag"]["status"] == "active"

    def test_agents_status_missing_tenant(self, client):
        """Test status sin tenant_id."""
        response = client.get("/api/v1/agents/status")
        assert response.status_code == 422
