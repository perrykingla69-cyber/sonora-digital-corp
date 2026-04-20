# agent:database-agent — Especialista Operaciones Base de Datos
> Carga solo este archivo. Para contexto cross-dominio: `mem_search "database agent"` en Engram.

## Dominio
Operaciones de base de datos: validación SQL, migraciones, pruebas RLS, backups.
Modelo: Determinístico primero (sqlparse, asyncpg) + fallback seguro.

## Archivo clave
- `main.py` — DatabaseAgent async lifecycle + 4 operaciones principales

## Operaciones soportadas
| Operación | Entrada | Salida |
|-----------|---------|--------|
| `validate_sql` | `{"sql": "SELECT...", "check_syntax": true, "check_rls": true}` | `{"valid": true, "errors": [], "warnings": [], "sql_hash": "abc123"}` |
| `apply_migration` | `{"migration_path": "001_init.sql", "dry_run": true}` | `{"success": true, "migration_id": "001_init", "duration_ms": 125}` |
| `test_rls` | `{"table": "invoices", "tenant_id": "uuid-1"}` | `{"rls_active": true, "policies": [...], "isolation_verified": true}` |
| `backup_database` | `{"format": "sql", "compress": true}` | `{"success": true, "backup_file": "backup-...sql.gz", "size_bytes": 524288, "checksum": "sha256:..."}` |

## Reglas críticas
- **Determinístico primero**: validación SQL usa `sqlparse` (sin LLM)
- **Async-first**: todas las operaciones son `async def` con `asyncpg`
- **Nunca inventa**: no especula sobre migraciones o RLS — solo reporta lo que existe
- **Fallback seguro**: si asyncpg no está disponible, devuelve estructura JSON válida con `warning`
- **Tenant-scoped**: operaciones pueden ser limitadas a un tenant específico

## Flujo
```
entrada (validate_sql|apply_migration|test_rls|backup_database)
  → operación específica async
  → si necesita BD: conectar con asyncpg
  → validación/transformación determinística
  → JSON → salida
```

## Dependencias
- asyncpg (conexión async a PostgreSQL)
- sqlparse (validación/parsing SQL)
- pydantic (config/schemas)
- pytest/pytest-asyncio (testing)
- python-dotenv (.env loading)
- PostgreSQL client tools (pg_dump para backups)

## Environment
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

## Tests (16 implementados)
- **TestSQLValidation** (7): syntax, RLS warnings, parameters, transactions, empty input, hash consistency
- **TestMigration** (5): dry_run, file_not_found, missing_path, idempotent, tenant_scoped
- **TestRLS** (4): missing_table, without_asyncpg, multi_tenant, policy_by_user
- **TestBackup** (3): missing_pg_dump, compress_option, creates_directory, checksum, tenant_suffix
- **TestAgent** (5): unknown_operation, get_input_empty, invalid_json, serialize_result
- **TestIntegration** (2): validate_sql_e2e, test_rls_e2e

## Nichos soportados
- `general` — Base de datos genérica (todas las operaciones)
- `fiscal` — Base de datos fiscal (validación RLS para reportes)
- `restaurante` — Base de datos restaurante (validación migración, backups)
- `constructor` — Base de datos construcción (RLS proyectos, migraciones)
