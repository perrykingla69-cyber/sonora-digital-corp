# CLAUDE-extended.md — Detalles Técnicos Completos

Esta es la versión extendida de CLAUDE.md para referencia profunda. Consulta aquí para:
- Stack técnico detallado
- Variables de entorno
- Gotchas específicos
- Configuración Docker completa

---

## 💾 STACK TÉCNICO DETALLADO

| Capa | Tecnología | Versión | Notas |
|------|------------|---------|-------|
| Backend API | FastAPI | 0.115.6 | Async (asyncio, asyncpg) |
| Lenguaje | Python | 3.11 | Type hints requeridos |
| ORM | SQLAlchemy | 2.0.36 | Async mode |
| Base de datos | PostgreSQL | 16-alpine | RLS active |
| Caché | Redis | 7-alpine | JWT revocation (JTI), rate limit |
| Vector DB | Qdrant | 1.9.2 | RAG/embeddings |
| LLM Local | Ollama | latest | DeepSeek-R1:1.5b |
| LLM Externo | OpenRouter API | - | google/gemini-2.0-flash-001 |
| Frontend | Next.js | 14.2.3 | App Router, TypeScript |
| Chat Local | Telegram | Bot 21.9 | 4 bots activos |
| Chat WhatsApp | Baileys | 6.7.21 | Sin dependencia API oficial |
| Automatización | N8N | latest | Workflows versionados |
| Auth | JWT + bcrypt | - | Field: `usuario` (NO `user`) |
| Infra | Docker Compose v2 | - | Local + VPS (variantes) |
| Web Server | Nginx | latest | Reverse proxy, HTTPS |

---

## ⚙️ VARIABLES DE ENTORNO (`infra/.env`)

```bash
# PostgreSQL
DB_USER=hermes
DB_PASSWORD=<SECRETO>
DB_NAME=hermes_db
DATABASE_URL=postgresql+asyncpg://hermes:PASS@hermes_postgres:5432/hermes_db

# Redis
REDIS_PASSWORD=<SECRETO>
REDIS_URL=redis://:PASS@hermes_redis:6379/0

# JWT
JWT_SECRET=<SECRETO_FUERTE_MIN_32_CHARS>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# APIs Externas
OPENROUTER_API_KEY=<SECRETO>       # LLM: Gemini Flash gratuito
ANTHROPIC_API_KEY=<SECRETO>        # Opcional

# Telegram (4 bots)
TELEGRAM_TOKEN_CEO=<TOKEN>
TELEGRAM_TOKEN_PUBLIC=<TOKEN>
TELEGRAM_TOKEN_HERMES=<TOKEN>
TELEGRAM_TOKEN_MYSTIC=<TOKEN>

# WhatsApp
WHATSAPP_NUMBER=+52-CHIP-TELCEL    # Número dedicado (PENDIENTE)

# MercadoPago
MP_ACCESS_TOKEN=<SECRETO>          # FALTANTE ⚠️

# Qdrant
QDRANT_API_KEY=hermes-qdrant-internal
QDRANT_URL=http://hermes_qdrant:6333

# Frontend
NEXT_PUBLIC_API_URL=http://hermes-api:8000
NEXT_PUBLIC_WS_URL=ws://hermes-api:8000
```

---

## 🐳 DOCKER COMPOSE — SERVICIOS COMPLETOS

**9 servicios + 5 volúmenes + 1 network**

```yaml
# CAPA 0: PERSISTENCIA
postgres:16-alpine         # BD principal (RLS)
redis:7-alpine            # Cache + JWT revocation
qdrant:v1.9.2             # Vector DB (RAG)

# CAPA 1: GATEWAYS
evolution:v2.2.3          # WhatsApp (Baileys)

# CAPA 2: ORQUESTACIÓN
n8n:latest                # Workflows automation

# CAPA 3: CEREBRO
hermes-api                # FastAPI backend (puerto 8000)
content-agent             # Generación de content (puerto 8001)

# CAPA 4: AGENTES
hermes-agent              # Orquestador (Telegram + IA)
mystic-agent              # Shadow analyst
clawbot                   # Bot ejecutor (puerto 3003)

# CAPA 5: FRONTEND
frontend                  # Next.js 14 (puerto 3000)

# NETWORK
hermes_net (bridge)       # Subnet: 172.21.0.0/16

# VOLUMES
postgres_data, redis_data, qdrant_data, 
evolution_data, n8n_data
```

---

## 🔒 SEGURIDAD — DETALLES

### PostgreSQL Row-Level Security (RLS)
```python
# En cada transacción:
async with db.begin():
    await db.execute(text("SET LOCAL app.current_tenant_id TO :tenant_id"), {"tenant_id": tenant_id})
    # RLS policies filtran automáticamente
```

⚠️ **Gotcha**: `SET LOCAL` es transaction-scoped (seguro con PgBouncer); `SET` global causa issues en conexión pooling.

### JWT + bcrypt
- Field: `usuario` (no `user`)
- Revocación por JTI en Redis (no stateless puro)
- bcrypt directo (NO passlib — incompatible)
- Expiración: 24 horas (configurable)

### Secretos
- `infra/.env` → gitignored
- `infra/.env.example` → template público
- Rotación documentada si se expone

---

## 📂 DIRECTORIOS DETALLADOS

### `/backend/` — LEGACY (Monolítico)
```
main.py (147KB)                    # API monolítica, 147 cálculos SAT
├── app/
│   ├── academy.py                 # ML/AI training logic
│   ├── ai/                        # Brain workflows, embeddings
│   ├── api/                       # Routers (deprecated)
│   ├── data/                      # Qdrant + memory integration
│   ├── fiscal_reasoning/          # Cálculos contables SAT
│   ├── omnichannel/               # WhatsApp, Telegram bridges
│   └── predictive/                # Forecasting models
├── models.py                       # ORM: usuarios, tenants, facturas
├── database.py                     # AsyncSession, RLS via SET LOCAL
└── security.py                     # JWT, bcrypt validation
```

### `/apps/api/` — V2 Bootstrap (Modular)
```
app/
├── main.py                         # FastAPI v2 bootstrap
├── agents/                         # Agent definitions
├── api/                            # V2 routers (modular)
├── core/                           # Config, dependencies
├── models/                         # SQLAlchemy v2 async
├── schemas/                        # Pydantic v2
├── services/                       # Business logic
└── webhooks/                       # Stripe, WhatsApp callbacks
```

### `/apps/hermes/` — HERMES Agent
```
agent.py                            # 🤖 Loop: polling Telegram + LLM
├── handlers/                       # Message processing
├── skills/                         # Commands (/code, /status, /deploy)
└── config.py
```

### `/apps/mystic/` — MYSTIC Agent
```
agent.py                            # 🧠 Análisis + alertas horarias
├── scanners/                       # Health check, market analysis
├── reporters/                      # Alert formatting
└── config.py
```

### `/frontend/` — Next.js 14
```
src/app/
├── [niche]/page.tsx               # 6 landings (restaurante, contador, etc.)
├── dashboard/                     # Dashboard principal
├── auth/                          # Login flow
└── layout.tsx                     # Root layout + providers
components/                         # React UI (Tailwind)
```

### `/infra/` — Infraestructura
```
docker-compose.yml                  # Stack local (11 servicios)
docker-compose.vps.yml             # Variante VPS
nginx/                              # Reverse proxy + HTTPS
sql/init/                           # Scripts inicialización
sql/migrations/                     # Alembic migrations
scripts/deploy.sh, wipe_vps.sh     # Automation
.env                                # Secretos (gitignored)
.env.example                        # Template público
```

---

## 🚨 GOTCHAS TÉCNICOS (Trampas Comunes)

### PostgreSQL + RLS
- ❌ `SET app.current_tenant_id = 'uuid'` (global) → falla con PgBouncer
- ✅ `SET LOCAL app.current_tenant_id = 'uuid'` (transaction-scoped)

### Tabla `cierres_mes`
- Columna `año` tiene ñ literal (no `anio`)
- En SQL: `SELECT * FROM cierres_mes WHERE año = 2026`

### bcrypt vs passlib
- ❌ `passlib` es incompatible con schema actual
- ✅ Usar `bcrypt` directo

### Ollama en VPS
- RAM limitada (~4GB disponible)
- Pausar si no está activo: `docker stop hermes_ollama`
- Modelos pesados (DeepSeek) requieren CPU decent

### Telegram Container
- Variable interna: `DEFAULT_BOT_TOKEN`
- Mapeada desde: `TELEGRAM_TOKEN` en infra/.env
- No editar directo en docker-compose; cambiar en .env

### N8N Workflows
- Versionados en `/infra/n8n-workflows/`
- Importar con N8N CLI o UI
- Integración con API webhooks en backend

### Frontend Rebuild
- Variables en `build.args` (docker-compose)
- NO en `environment` (esos son runtime)
- Rebuild necesario para variables `NEXT_PUBLIC_*`

### Legacy main.py — Pesado
- 147KB monolítico → causa overhead en development
- Estrategia: `apps/api/` v2 en paralelo, migrar routers incrementalmente

---

## 📋 PENDIENTES CRÍTICOS (Actualizado 2026-04-14)

### 🔴 Credenciales Faltantes (Bloquean features)
- `MP_ACCESS_TOKEN` — MercadoPago (generar en developers.mercadopago.com)
- `ANTHROPIC_API_KEY` — Opcional (si activamos Claude API)
- `WHATSAPP_NUMBER` — Chip Telcel dedicado (aún no asignado)

### 🟡 En Progreso
- Modularizar backend legacy → routers v2 en `apps/api/`
- Memory layer formalizado (Qdrant RAG)
- Runtime de agentes + skills registry

### ✅ Completado Recientemente
- Rebrand MYSTIC→HERMES
- Docker Compose v2 stack (11 servicios)
- PostgreSQL RLS multi-tenant
- JWT con revocación por JTI
- OpenRouter integrado (free tier)
- GitHub Actions CI/CD → VPS deploy

---

## 🔄 FLUJO DE TRABAJO — COLABORACIÓN

1. **Leer primero**: `docs/secure_deploy_workflow.md` + CLAUDE.md
2. **Verificar estado**: `git status`, rama actual, último commit
3. **Declarar cambios**: Línea explicativa del archivo/directorio a tocar
4. **Cambios pequeños**: Verificables, con rollback claro
5. **Reportar siempre**: Diff, comandos, riesgos, siguiente acción
6. **Tests**: Correr mínimos (`pytest`) antes de push a `main`

---

**Última actualización**: 2026-04-14  
**Referencia**: CLAUDE.md (compacto) ← → CLAUDE-extended.md (detallado)
