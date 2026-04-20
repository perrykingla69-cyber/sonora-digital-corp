# Database Agent — HERMES OS

Agent especializado en operaciones de base de datos: validación SQL, migraciones, pruebas RLS, backups.

## Inicio Rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
pytest tests/test_agent.py -v

# Build Docker
docker build -t database-agent:latest .

# Ejecutar con Docker
echo '{"operation":"validate_sql","data":{"sql":"SELECT * FROM users WHERE tenant_id = $1"}}' \
  | docker run -i database-agent:latest
```

## Operaciones

### 1. validate_sql
Valida sintaxis SQL y cumplimiento RLS.

```json
{
  "operation": "validate_sql",
  "data": {
    "sql": "SELECT * FROM users WHERE tenant_id = $1",
    "check_syntax": true,
    "check_rls": true
  }
}
```

**Respuesta:**
```json
{
  "operation": "validate_sql",
  "valid": true,
  "errors": [],
  "warnings": [],
  "sql_hash": "abc123",
  "sql_length": 40
}
```

### 2. apply_migration
Aplica migraciones de base de datos.

```json
{
  "operation": "apply_migration",
  "data": {
    "migration_path": "migrations/001_init.sql",
    "dry_run": true,
    "tenant_id": "optional-tenant-uuid"
  }
}
```

**Respuesta:**
```json
{
  "operation": "apply_migration",
  "success": true,
  "migration_id": "001_init",
  "rows_affected": 0,
  "duration_ms": 125,
  "tenant_scoped": false,
  "dry_run": true
}
```

### 3. test_rls
Prueba políticas RLS y aislamiento multi-tenant.

```json
{
  "operation": "test_rls",
  "data": {
    "table": "invoices",
    "tenant_id": "uuid-1",
    "test_user_id": "user-1",
    "expected_row_count": 5
  }
}
```

**Respuesta:**
```json
{
  "operation": "test_rls",
  "table": "invoices",
  "rls_active": true,
  "policies": ["rls_select", "rls_update"],
  "test_passed": true,
  "actual_row_count": 5,
  "isolation_verified": true,
  "policy_count": 2
}
```

### 4. backup_database
Crea backup de base de datos.

```json
{
  "operation": "backup_database",
  "data": {
    "format": "sql",
    "compress": true,
    "backup_dir": "/backups",
    "tenant_id": "optional-tenant-uuid"
  }
}
```

**Respuesta:**
```json
{
  "operation": "backup_database",
  "success": true,
  "backup_file": "backup-2026-04-20T14:30:00Z.sql.gz",
  "size_bytes": 524288,
  "tables_backed_up": 18,
  "duration_ms": 2450,
  "checksum": "sha256:abc123",
  "compressed": true
}
```

## Configuración

Variables de entorno (.env):

```
DATABASE_URL=postgresql://user:pass@postgres:5432/hermes_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=hermes_db
BACKUP_DIR=/backups
BACKUP_RETENTION_DAYS=30
ENVIRONMENT=production
```

## Testing

29 tests cubren:
- **SQL Validation**: 7 tests (syntax, RLS warnings, parameters, transactions)
- **Migrations**: 5 tests (dry-run, errors, idempotence, tenant-scoping)
- **RLS**: 4 tests (policy detection, multi-tenant isolation)
- **Backups**: 5 tests (file creation, compression, checksums)
- **Agent Core**: 6 tests (input/output, serialization)
- **Integration**: 2 tests (end-to-end operations)

```bash
pytest tests/test_agent.py -v
# Result: 29 passed in 4.86s
```

## Docker

```bash
# Build
docker build -t database-agent:latest .

# Run
docker run -e DATABASE_URL=postgresql://... database-agent:latest

# Interactive (with stdin)
echo '{"operation":"validate_sql","data":{"sql":"SELECT 1"}}' \
  | docker run -i database-agent:latest
```

## Integración con HERMES

Para integrar con orquestador HERMES:

```python
# En HERMES orchestrator
import json
import subprocess

def call_database_agent(operation: str, data: dict) -> dict:
    payload = {
        "operation": operation,
        "data": data
    }
    result = subprocess.run(
        ["docker", "run", "-i", "database-agent:latest"],
        input=json.dumps(payload),
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

# Uso
result = call_database_agent("validate_sql", {
    "sql": "SELECT * FROM users WHERE tenant_id = $1",
    "check_rls": True
})
```

## Documentación Completa

Ver `CLAUDE.md` para documentación interna detallada.

## Licencia

Parte de HERMES OS — Sonora Digital Corp
