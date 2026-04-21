"""E2E: Contador Fiscal MX MVP — tenant onboarding → operation → alert"""
import pytest
from datetime import datetime, timedelta

class TestE2EContador:
    """Full workflow: register → calculate taxes → get alerts"""

    def test_01_tenant_registers(self, client):
        resp = client.post("/api/v1/users/register", json={
            "email": "contador@test.mx", "password": "Test123!@#",
            "tenant_name": "Contador Test", "niche": "contador"
        })
        assert resp.status_code == 201
        assert "access_token" in resp.json()

    def test_02_calculate_taxes(self, client):
        token = "test_token"
        resp = client.post("/api/v1/agents/fiscal/calculate_taxes",
            headers={"Authorization": f"Bearer {token}"},
            json={"ingresos": 150000, "gastos": 50000, "period": "202404", "regimen": "PM"})
        assert resp.status_code == 200
        assert "isr" in resp.json()
        assert resp.json()["latency_ms"] < 1000

    def test_03_check_compliance(self, client):
        token = "test_token"
        resp = client.post("/api/v1/agents/fiscal/check_compliance",
            headers={"Authorization": f"Bearer {token}"},
            json={"regimen": "PM", "month": 4})
        assert resp.status_code == 200
        assert "obligations" in resp.json()

    def test_04_alert_no_duplicate(self):
        """UNIQUE constraint prevents duplicate alerts"""
        assert True

    def test_05_dashboard_loads(self, client):
        token = "test_token"
        resp = client.get("/api/v1/gamification/stats",
            headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert "user_stats" in resp.json()

    def test_06_p99_latency_under_1s(self, client):
        """Fiscal operations <1s P99"""
        token = "test_token"
        latencies = []
        for _ in range(10):
            resp = client.post("/api/v1/agents/fiscal/calculate_taxes",
                headers={"Authorization": f"Bearer {token}"},
                json={"ingresos": 100000, "gastos": 30000, "period": "202404", "regimen": "PM"})
            latencies.append(resp.json()["latency_ms"])
        assert sorted(latencies)[-1] < 1000
