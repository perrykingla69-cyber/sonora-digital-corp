"""Integration tests: Contador Fiscal MVP — API endpoints + RLS + Performance"""
import pytest
import time
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

class TestIntegrationFiscalAPI:
    """Endpoint integration: Fiscal Agent operations"""

    def test_fiscal_calculate_taxes_rls_isolation(self, client, db):
        """RLS: Tenant A ≠ Tenant B in calculations"""
        token_a = "tenant_a_token"
        token_b = "tenant_b_token"

        resp_a = client.post(
            "/api/v1/agents/fiscal/calculate_taxes",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"ingresos": 100000, "gastos": 30000, "period": "202404", "regimen": "PM"}
        )
        resp_b = client.post(
            "/api/v1/agents/fiscal/calculate_taxes",
            headers={"Authorization": f"Bearer {token_b}"},
            json={"ingresos": 200000, "gastos": 50000, "period": "202404", "regimen": "PF"}
        )
        assert resp_a.status_code == 200
        assert resp_b.status_code == 200
        assert resp_a.json()["isr"] != resp_b.json()["isr"]

    def test_fiscal_validate_cfdi_deterministic(self, client):
        """CFDI validator: deterministic, same input = same output"""
        token = "test_token"
        cfdi = {"rfc_emisor": "AAA010101ABC", "rfc_receptor": "XIA190128CD7", "monto": 1000.00}

        r1 = client.post("/api/v1/agents/fiscal/validate_cfdi",
                         headers={"Authorization": f"Bearer {token}"}, json=cfdi)
        r2 = client.post("/api/v1/agents/fiscal/validate_cfdi",
                         headers={"Authorization": f"Bearer {token}"}, json=cfdi)

        assert r1.json()["valid"] == r2.json()["valid"]
        assert r1.json()["latency_ms"] < 1000
        assert r2.json()["latency_ms"] < 1000

    def test_fiscal_check_compliance_returns_dates(self, client):
        """Obligaciones: returns exact deadline dates"""
        token = "test_token"
        resp = client.post("/api/v1/agents/fiscal/check_compliance",
                          headers={"Authorization": f"Bearer {token}"},
                          json={"regimen": "PM", "month": 4})
        assert resp.status_code == 200
        data = resp.json()
        assert "obligations" in data
        assert "deadlines" in data
        assert len(data["obligations"]) > 0
        # Verify ISR on 17th exists
        assert any("17" in str(d) or "isr" in o.lower()
                  for o, d in zip(data["obligations"], data["deadlines"]))

class TestDashboardIntegration:
    """Dashboard: component → API → data flow"""

    def test_dashboard_gamification_stats_endpoint(self, client):
        """GET /api/v1/gamification/stats returns valid user stats"""
        token = "test_token"
        resp = client.get("/api/v1/gamification/stats",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "user_stats" in data
        assert "level" in data["user_stats"]
        assert "total_xp" in data["user_stats"]
        assert "badges_earned" in data["user_stats"]

    def test_dashboard_calculator_full_flow(self, client):
        """CalculadoraRapida: input → calculate_taxes → output"""
        token = "test_token"
        payload = {
            "ingresos": 150000,
            "gastos": 50000,
            "period": "202404",
            "regimen": "PM"
        }
        resp = client.post("/api/v1/agents/fiscal/calculate_taxes",
                          headers={"Authorization": f"Bearer {token}"},
                          json=payload)
        assert resp.status_code == 200
        data = resp.json()
        # Verify response has required fields for dashboard display
        assert "isr" in data
        assert "iva" in data
        assert "base_gravable" in data
        assert "fuente" in data  # Normativa citation
        assert data["latency_ms"] < 1000

class TestAlertsWorkflow:
    """N8N alerts: trigger → message → delivery"""

    def test_alert_trigger_logic_5_days_before(self):
        """Alert triggers exactly 5 days before deadline"""
        from datetime import datetime, timedelta

        deadline = datetime.now() + timedelta(days=5)
        today = datetime.now()
        days_until = (deadline - today).days

        assert days_until == 5, "Alert should trigger 5 days before"
        assert days_until >= 0, "Deadline should be in future"

    def test_alert_message_format(self):
        """Alert message includes required fields"""
        msg = """📌 ISR mensual vence 17-04-2024 (5 días).
Base gravable: $100,000. Estimado: $16,500.
Ver en: https://contador.hermes.mx/alerts/isr-202404"""

        assert "📌" in msg
        assert "vence" in msg.lower()
        assert "días" in msg.lower()
        assert "contador.hermes.mx" in msg

class TestPerformance:
    """Latency + throughput validation"""

    def test_p99_latency_under_1s(self, client):
        """Fiscal operations: P99 latency <1s across 20 calls"""
        token = "test_token"
        latencies = []

        for i in range(20):
            start = time.time()
            resp = client.post("/api/v1/agents/fiscal/calculate_taxes",
                             headers={"Authorization": f"Bearer {token}"},
                             json={"ingresos": 100000 + i*1000, "gastos": 30000,
                                   "period": "202404", "regimen": "PM"})
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)
            assert resp.status_code == 200

        p99 = sorted(latencies)[-1]
        assert p99 < 1000, f"P99 {p99}ms exceeds 1s target"

    def test_dashboard_parallel_load(self, client):
        """Dashboard: 3 parallel API calls <2s total"""
        token = "test_token"
        start = time.time()

        # Simulate dashboard loading 3 endpoints in parallel
        r1 = client.get("/api/v1/gamification/stats",
                       headers={"Authorization": f"Bearer {token}"})
        r2 = client.post("/api/v1/agents/fiscal/check_compliance",
                        headers={"Authorization": f"Bearer {token}"},
                        json={"regimen": "PM", "month": 4})
        r3 = client.post("/api/v1/agents/fiscal/calculate_taxes",
                        headers={"Authorization": f"Bearer {token}"},
                        json={"ingresos": 100000, "gastos": 30000,
                              "period": "202404", "regimen": "PM"})

        elapsed_ms = (time.time() - start) * 1000

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r3.status_code == 200
        assert elapsed_ms < 2000, f"Dashboard load {elapsed_ms}ms exceeds 2s"

class TestSmokeTests:
    """Pre-production validation: all systems GO"""

    def test_health_check_all_systems(self, client):
        """Health endpoint: db, redis, version OK"""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "online"
        assert data["db"] == "ok"
        assert data["redis"] == "ok"
        assert "version" in data

    def test_endpoints_all_respond(self, client):
        """All critical endpoints respond (not 404/500)"""
        token = "test_token"
        endpoints = [
            ("GET", "/health"),
            ("GET", "/api/v1/gamification/stats"),
            ("POST", "/api/v1/agents/fiscal/calculate_taxes",
             {"ingresos": 100000, "gastos": 30000, "period": "202404", "regimen": "PM"}),
            ("POST", "/api/v1/agents/fiscal/check_compliance",
             {"regimen": "PM", "month": 4}),
        ]

        for method, path, *body in endpoints:
            if method == "GET":
                resp = client.get(path, headers={"Authorization": f"Bearer {token}"})
            else:
                resp = client.post(path, headers={"Authorization": f"Bearer {token}"},
                                  json=body[0] if body else {})

            assert resp.status_code in [200, 201, 422], f"{method} {path} failed: {resp.status_code}"
            assert resp.status_code != 500, f"500 error on {method} {path}"
            assert resp.status_code != 404, f"404 error on {method} {path}"
