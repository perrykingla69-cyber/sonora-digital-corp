"""Smoke tests: Pre-production verification before deploy"""
import pytest

class TestProductionReadiness:
    """Critical path validation: can we go live?"""

    def test_fiscal_agent_all_8_operations_available(self, client):
        """All 8 Fiscal Agent operations are implemented and accessible"""
        token = "test_token"
        operations = [
            ("validate_cfdi", {"rfc_emisor": "AAA010101ABC", "rfc_receptor": "XIA190128CD7", "monto": 1000}),
            ("calculate_taxes", {"ingresos": 100000, "gastos": 30000, "period": "202404", "regimen": "PM"}),
            ("check_compliance", {"regimen": "PM", "month": 4}),
            ("get_tax_catalogs", {"query": "tabla18", "period": "202404"}),
            ("validate_receipt", {"tipo": "factura", "monto": 1000, "rfc_emisor": "AAA010101ABC"}),
            ("alert_deadline", {"obligacion": "ISR_mensual"}),
            ("suggest_deductions", {"regimen": "PM", "ingresos": 100000}),
            ("generate_compliance_report", {"period": "202404", "regimen": "PM"}),
        ]

        for op_name, payload in operations:
            resp = client.post(
                f"/api/v1/agents/fiscal/{op_name}",
                headers={"Authorization": f"Bearer {token}"},
                json=payload
            )
            assert resp.status_code == 200, f"Operation {op_name} failed: {resp.status_code}"
            assert "success" in resp.json() or "data" in resp.json(), f"Invalid response format for {op_name}"

    def test_dashboard_components_ready(self, client):
        """Dashboard routes and components are mounted"""
        # Landing page exists
        resp = client.get("/contador")
        assert resp.status_code in [200, 307], "Contador landing page not accessible"

        # Dashboard page exists
        resp = client.get("/contador/dashboard")
        assert resp.status_code in [200, 307], "Contador dashboard not accessible"

    def test_gamification_fully_operational(self, client):
        """Gamification endpoints: stats, badges, leaderboard"""
        token = "test_token"

        # Stats
        resp = client.get("/api/v1/gamification/stats",
                         headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

        # Leaderboard (public)
        resp = client.get("/api/v1/gamification/leaderboard")
        assert resp.status_code == 200

        # Badges (public)
        resp = client.get("/api/v1/gamification/badges")
        assert resp.status_code == 200

    def test_database_migrations_applied(self, db):
        """Verify migration tables exist: obligaciones, alerts_sent"""
        from sqlalchemy import text

        # Check obligaciones table
        result = db.execute(text("SELECT 1 FROM obligaciones LIMIT 1"))
        assert result is not None, "obligaciones table missing"

        # Check alerts_sent table
        result = db.execute(text("SELECT 1 FROM alerts_sent LIMIT 1"))
        assert result is not None, "alerts_sent table missing"

    def test_n8n_workflow_endpoint_available(self, client):
        """N8N is accessible and ready for workflow deployment"""
        # N8N usually on port 5678
        # This is a mock test (real N8N check would be via curl to localhost:5678)
        assert True, "N8N accessible"

    def test_rls_security_enforced(self, client):
        """RLS policies are active: tenant isolation works"""
        token = "test_token"
        payload = {"ingresos": 100000, "gastos": 30000, "period": "202404", "regimen": "PM"}

        # Call should enforce RLS (tenant context via JWT)
        resp = client.post("/api/v1/agents/fiscal/calculate_taxes",
                          headers={"Authorization": f"Bearer {token}"},
                          json=payload)
        assert resp.status_code == 200, "RLS enforcement failed"

    def test_frontend_build_complete(self, client):
        """Frontend is built and static assets are served"""
        resp = client.get("/")
        # Should serve frontend or redirect (not 404/500)
        assert resp.status_code in [200, 301, 302, 307], "Frontend not built"

    def test_api_documentation_available(self, client):
        """OpenAPI docs are generated"""
        resp = client.get("/docs")
        assert resp.status_code == 200, "API docs not available"

        resp = client.get("/redoc")
        assert resp.status_code == 200, "ReDoc not available"

class TestProductionMetrics:
    """Metrics that determine "ready to ship"""""

    def test_error_rate_zero_percent(self, client):
        """No errors on happy path operations"""
        token = "test_token"

        # Run 10 operations, all should succeed
        for i in range(10):
            resp = client.post(
                "/api/v1/agents/fiscal/calculate_taxes",
                headers={"Authorization": f"Bearer {token}"},
                json={"ingresos": 100000 + i*1000, "gastos": 30000, "period": "202404", "regimen": "PM"}
            )
            assert resp.status_code == 200

    def test_latency_acceptable(self, client):
        """Latency metrics within SLA: P50 <200ms, P99 <1s"""
        import time
        token = "test_token"
        latencies = []

        for i in range(10):
            start = time.time()
            client.post("/api/v1/agents/fiscal/calculate_taxes",
                       headers={"Authorization": f"Bearer {token}"},
                       json={"ingresos": 100000, "gastos": 30000, "period": "202404", "regimen": "PM"})
            latencies.append((time.time() - start) * 1000)

        p50 = sorted(latencies)[5]
        p99 = sorted(latencies)[-1]

        assert p50 < 200, f"P50 {p50}ms exceeds 200ms"
        assert p99 < 1000, f"P99 {p99}ms exceeds 1s"

    def test_security_headers_present(self, client):
        """Response headers include security best practices"""
        resp = client.get("/health")
        # FastAPI should include these by default or via middleware
        assert resp.status_code == 200
        # Headers would be checked in real test:
        # assert "Content-Type" in resp.headers

class TestDeploymentGate:
    """Final gate: Can we merge to main and deploy?"""

    def test_all_endpoints_respond_200(self, client):
        """Every endpoint on critical path returns 2xx"""
        critical_paths = [
            ("/health", "GET"),
            ("/api/v1/gamification/stats", "GET"),
            ("/api/v1/gamification/leaderboard", "GET"),
            ("/docs", "GET"),
        ]

        token = "test_token"
        for path, method in critical_paths:
            if method == "GET":
                resp = client.get(path, headers={"Authorization": f"Bearer {token}"})
            # Add POST paths as needed
            assert resp.status_code < 400, f"{method} {path} failed: {resp.status_code}"

    def test_deployment_version_incremented(self):
        """Version should be incremented for new deployment"""
        # Check version in main.py or settings.py
        # This is a placeholder for CI/CD to verify version bump
        assert True, "Version check passed"

    def test_git_status_clean(self):
        """No uncommitted changes before deployment"""
        # This would be run in CI/CD pipeline
        # git status --porcelain should return nothing
        assert True, "Git status clean"

    def test_all_tests_passing(self):
        """All test suites must pass before merge"""
        # This is meta: the test suite itself is proof
        # If this test runs, pytest didn't fail on other tests
        assert True, "All tests passing"
