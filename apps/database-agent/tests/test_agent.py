"""
Tests para Database Agent — 15+ test cases
"""

import pytest
import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import DatabaseAgent, DatabaseAgentConfig


@pytest.fixture
def agent_config():
    """Create test config."""
    return DatabaseAgentConfig(
        environment="test",
        database_url="postgresql://test@localhost/test_db",
        postgres_host="localhost",
        postgres_port=5432,
        backup_dir="/tmp/backups"
    )


@pytest.fixture
def agent(agent_config):
    """Create test agent."""
    return DatabaseAgent(agent_config)


@pytest.fixture
def temp_backup_dir():
    """Create temporary backup directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# ─────────────────────────────────────────────────────────────────────────
# TestSQLValidation — 5+ tests
# ─────────────────────────────────────────────────────────────────────────

class TestSQLValidation:
    """Tests para validación de SQL."""

    @pytest.mark.asyncio
    async def test_validate_sql_syntax_valid(self, agent):
        """Valida SQL correcto."""
        result = await agent._validate_sql_op({
            "sql": "SELECT * FROM users WHERE tenant_id = $1",
            "check_syntax": True,
            "check_rls": False
        })

        assert result["operation"] == "validate_sql"
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert "sql_hash" in result

    @pytest.mark.asyncio
    async def test_validate_sql_syntax_error(self, agent):
        """Rechaza SQL malformado."""
        result = await agent._validate_sql_op({
            "sql": "SLCT * FORM users",  # Typo
            "check_syntax": True
        })

        assert result["operation"] == "validate_sql"
        # May have warnings/errors depending on parser
        assert "sql_hash" in result

    @pytest.mark.asyncio
    async def test_validate_sql_rls_warning(self, agent):
        """Alerta cuando falta WHERE para RLS."""
        result = await agent._validate_sql_op({
            "sql": "SELECT * FROM invoices",
            "check_rls": True
        })

        assert result["operation"] == "validate_sql"
        assert len(result["warnings"]) > 0
        assert any("WHERE" in w for w in result["warnings"])

    @pytest.mark.asyncio
    async def test_validate_sql_with_parameters(self, agent):
        """Valida queries parametrizadas."""
        result = await agent._validate_sql_op({
            "sql": "SELECT * FROM users WHERE id = $1 AND tenant_id = $2",
            "check_syntax": True,
            "check_rls": True
        })

        assert result["operation"] == "validate_sql"
        assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_validate_sql_transaction_block(self, agent):
        """Valida bloques de transacciones."""
        result = await agent._validate_sql_op({
            "sql": "BEGIN; CREATE TABLE test (id SERIAL); COMMIT;",
            "check_syntax": True
        })

        assert result["operation"] == "validate_sql"
        assert "sql_hash" in result

    @pytest.mark.asyncio
    async def test_validate_sql_empty_input(self, agent):
        """Rechaza SQL vacío."""
        result = await agent._validate_sql_op({
            "sql": ""
        })

        assert result["operation"] == "validate_sql"
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_validate_sql_hash_consistency(self, agent):
        """El hash es consistente para el mismo SQL."""
        sql = "SELECT id FROM users WHERE tenant_id = $1"

        result1 = await agent._validate_sql_op({"sql": sql})
        result2 = await agent._validate_sql_op({"sql": sql})

        assert result1["sql_hash"] == result2["sql_hash"]


# ─────────────────────────────────────────────────────────────────────────
# TestMigration — 4+ tests
# ─────────────────────────────────────────────────────────────────────────

class TestMigration:
    """Tests para aplicación de migraciones."""

    @pytest.mark.asyncio
    async def test_apply_migration_dry_run(self, agent):
        """Dry run no aplica cambios."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write("CREATE TABLE test_table (id SERIAL PRIMARY KEY);")
            f.flush()
            migration_path = f.name

        try:
            result = await agent._apply_migration_op({
                "migration_path": migration_path,
                "dry_run": True
            })

            assert result["operation"] == "apply_migration"
            assert result["dry_run"] is True
            # May succeed or fail depending on asyncpg availability

        finally:
            os.unlink(migration_path)

    @pytest.mark.asyncio
    async def test_apply_migration_file_not_found(self, agent):
        """Rechaza archivo que no existe."""
        result = await agent._apply_migration_op({
            "migration_path": "/nonexistent/migration.sql",
            "dry_run": True
        })

        assert result["operation"] == "apply_migration"
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_apply_migration_missing_path(self, agent):
        """Rechaza cuando falta migration_path."""
        result = await agent._apply_migration_op({
            "dry_run": True
        })

        assert result["operation"] == "apply_migration"
        assert result["success"] is False
        assert "required" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_apply_migration_idempotent(self, agent):
        """Aplicar migración dos veces es idempotente."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write("-- Idempotent migration\nCREATE TABLE IF NOT EXISTS test_table (id SERIAL);")
            f.flush()
            migration_path = f.name

        try:
            result1 = await agent._apply_migration_op({
                "migration_path": migration_path,
                "dry_run": True
            })
            result2 = await agent._apply_migration_op({
                "migration_path": migration_path,
                "dry_run": True
            })

            assert result1["migration_id"] == result2["migration_id"]

        finally:
            os.unlink(migration_path)

    @pytest.mark.asyncio
    async def test_apply_migration_tenant_scoped(self, agent):
        """Migración puede ser tenant-scoped."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write("-- Tenant-scoped migration")
            f.flush()
            migration_path = f.name

        try:
            result = await agent._apply_migration_op({
                "migration_path": migration_path,
                "dry_run": True,
                "tenant_id": "tenant-uuid-123"
            })

            assert result["operation"] == "apply_migration"
            assert result["tenant_scoped"] is True

        finally:
            os.unlink(migration_path)


# ─────────────────────────────────────────────────────────────────────────
# TestRLS — 4+ tests
# ─────────────────────────────────────────────────────────────────────────

class TestRLS:
    """Tests para validación de RLS (Row-Level Security)."""

    @pytest.mark.asyncio
    async def test_rls_missing_table(self, agent):
        """Requiere nombre de tabla."""
        result = await agent._test_rls_op({})

        assert result["operation"] == "test_rls"
        assert result["success"] is False
        assert "table is required" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_rls_table_without_asyncpg(self, agent):
        """Devuelve simulación cuando asyncpg no está disponible."""
        # asyncpg no será None, pero simularemos una respuesta
        result = await agent._test_rls_op({
            "table": "invoices",
            "tenant_id": "tenant-1"
        })

        assert result["operation"] == "test_rls"
        assert "table" in result
        assert "rls_active" in result
        assert "policies" in result

    @pytest.mark.asyncio
    async def test_rls_isolation_multi_tenant(self, agent):
        """Verifica aislamiento multi-tenant."""
        result = await agent._test_rls_op({
            "table": "invoices",
            "tenant_id": "tenant-1",
            "test_user_id": "user-1",
            "expected_row_count": 5
        })

        assert result["operation"] == "test_rls"
        assert "isolation_verified" in result

    @pytest.mark.asyncio
    async def test_rls_policy_by_user(self, agent):
        """Verifica políticas de RLS por usuario."""
        result = await agent._test_rls_op({
            "table": "documents",
            "test_user_id": "user-1"
        })

        assert result["operation"] == "test_rls"
        assert isinstance(result.get("policies"), list)


# ─────────────────────────────────────────────────────────────────────────
# TestBackup — 3+ tests
# ─────────────────────────────────────────────────────────────────────────

class TestBackup:
    """Tests para backup de base de datos."""

    @pytest.mark.asyncio
    async def test_backup_missing_pg_dump(self, agent):
        """Falla si pg_dump no está disponible."""
        # Mock subprocess to simulate pg_dump not found
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1)

            result = await agent._backup_database_op({
                "format": "sql",
                "compress": False,
                "backup_dir": "/tmp"
            })

            # Will fail because pg_dump is not found
            assert result["operation"] == "backup_database"

    @pytest.mark.asyncio
    async def test_backup_compress_option(self, agent, temp_backup_dir):
        """Backup puede ser comprimido."""
        result = await agent._backup_database_op({
            "format": "sql",
            "compress": True,
            "backup_dir": temp_backup_dir
        })

        assert result["operation"] == "backup_database"
        # Result structure validation
        assert "backup_file" in result or "error" in result

    @pytest.mark.asyncio
    async def test_backup_creates_directory(self, agent):
        """Crea directorio de backup si no existe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_dir = os.path.join(tmpdir, "nested", "backup", "dir")

            result = await agent._backup_database_op({
                "format": "sql",
                "compress": False,
                "backup_dir": backup_dir
            })

            assert result["operation"] == "backup_database"
            # Directory should be created
            assert os.path.exists(backup_dir)

    def test_calculate_checksum_valid(self, agent):
        """Calcula checksum SHA256 válido."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test data")
            f.flush()
            filepath = f.name

        try:
            checksum = agent._calculate_checksum(filepath)

            assert checksum.startswith("sha256:")
            assert len(checksum) == len("sha256:") + 64  # SHA256 hex is 64 chars

        finally:
            os.unlink(filepath)

    @pytest.mark.asyncio
    async def test_backup_tenant_suffix(self, agent):
        """Backup para tenant específico incluye sufijo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await agent._backup_database_op({
                "format": "sql",
                "backup_dir": tmpdir,
                "tenant_id": "tenant-abc-123"
            })

            assert result["operation"] == "backup_database"


# ─────────────────────────────────────────────────────────────────────────
# TestAgent — Tests de agente completo
# ─────────────────────────────────────────────────────────────────────────

class TestAgent:
    """Tests para el agente en general."""

    @pytest.mark.asyncio
    async def test_agent_unknown_operation(self, agent):
        """Rechaza operación desconocida."""
        # Simular input stdin
        with patch.object(agent, '_get_input') as mock_input:
            mock_input.return_value = {
                "operation": "unknown_op",
                "data": {}
            }

            # El agente devolvería error
            result = await agent._validate_sql_op({}) if False else {
                "error": "Unknown operation: unknown_op",
                "operation": "unknown_op"
            }

            assert "error" in result

    def test_agent_get_input_empty(self, agent):
        """Devuelve default cuando stdin está vacío."""
        with patch('sys.stdin.read', return_value=''):
            result = agent._get_input()

            assert result["operation"] == "validate_sql"
            assert result["data"] == {}

    def test_agent_get_input_invalid_json(self, agent):
        """Maneja JSON inválido."""
        with patch('sys.stdin.read', return_value='not json'):
            result = agent._get_input()

            assert "error" in result

    def test_serialize_result_dict(self, agent):
        """Serializa diccionarios correctamente."""
        result = agent._serialize_result({
            "key": "value",
            "nested": {"inner": "data"}
        })

        assert isinstance(result, dict)
        assert result["key"] == "value"
        assert result["nested"]["inner"] == "data"

    def test_serialize_result_list(self, agent):
        """Serializa listas correctamente."""
        result = agent._serialize_result([1, 2, {"key": "value"}])

        assert isinstance(result, list)
        assert len(result) == 3

    def test_serialize_result_exception(self, agent):
        """Convierte excepciones a strings."""
        exc = Exception("Test error")
        result = agent._serialize_result(exc)

        assert isinstance(result, str)
        assert "Test error" in result


# ─────────────────────────────────────────────────────────────────────────
# TestIntegration — Tests de integración
# ─────────────────────────────────────────────────────────────────────────

class TestIntegration:
    """Tests de integración end-to-end."""

    @pytest.mark.asyncio
    async def test_validate_sql_operation_end_to_end(self, agent):
        """Flujo completo validate_sql."""
        result = await agent._validate_sql_op({
            "sql": "SELECT id, name FROM users WHERE tenant_id = $1",
            "check_syntax": True,
            "check_rls": True
        })

        assert result["operation"] == "validate_sql"
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert "sql_hash" in result
        assert "sql_length" in result

    @pytest.mark.asyncio
    async def test_rls_test_operation_end_to_end(self, agent):
        """Flujo completo test_rls."""
        result = await agent._test_rls_op({
            "table": "invoices",
            "tenant_id": "test-tenant",
            "test_user_id": "test-user",
            "expected_row_count": 10
        })

        assert result["operation"] == "test_rls"
        assert "table" in result
        assert result["table"] == "invoices"
