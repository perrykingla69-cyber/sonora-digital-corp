# agent:api — Backend FastAPI
> Carga solo este archivo. Para contexto cross-dominio: `mem_search "hermes api"` en Engram.

## Dominio
API REST principal: auth, tenants, facturas, cierre, brain IA, webhooks.

## Archivos clave
- `main.py` — FastAPI app, routers, middleware
- `app/` — módulos de negocio (si existe)
- `database.py` — async SQLAlchemy + `SET LOCAL app.current_tenant_id` (RLS)
- `security.py` — JWT con field `usuario`, revocación por JTI en Redis
- `models.py` — ORM models (tabla `cierres_mes` tiene columna `año` con ñ)
- `schemas.py` — Pydantic schemas
- `migrations/` → usar Alembic

## Reglas críticas
- RLS: siempre `SET LOCAL` (no `SET`) — es transaction-scoped, PgBouncer-safe
- JWT: field `usuario` (no `user`), revocación por JTI en Redis
- bcrypt directo (no passlib — incompatible)
- No usar `print()` — solo `logging`
- Type hints obligatorios en funciones públicas
- Puerto: `8000`; health: `GET /status`

## ENV vars propias
`DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `OPENROUTER_API_KEY`

## Tests
`cd backend && pytest tests/`
