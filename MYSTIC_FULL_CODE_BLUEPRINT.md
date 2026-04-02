# MYSTIC FULL CODE BLUEPRINT v3.1
> Sonora Digital Corp | 19 Marzo 2026 | Para revisión Ingeniero de Sistemas
> VPS: 187.124.85.191 (Ubuntu 4GB RAM) | Dominio: sonoradigitalcorp.com
> Repo: github.com/perrykingla69-cyber/sonora-digital-corp | Rama: main

---

## 1. ESTRUCTURA COMPLETA DEL PROYECTO

```
sonora-digital-corp/
│
├── backend/
│   ├── main.py                        ← API completa FastAPI (todo en un archivo)
│   ├── models.py                      ← Modelos SQLAlchemy (15 tablas)
│   ├── schemas.py                     ← Pydantic schemas (request/response)
│   ├── database.py                    ← Conexión PostgreSQL via SQLAlchemy
│   ├── security.py                    ← JWT auth + bcrypt + roles
│   ├── calculos.py                    ← IVA, ISR, IEPS básicos
│   ├── calculos_completos_147.py      ← 147 cálculos fiscales SAT-compliant
│   ├── mve_validator.py               ← Validador Manifestación de Valor
│   ├── requirements.txt               ← Dependencias Python
│   ├── Dockerfile                     ← Imagen API
│   └── app/
│       └── ai/
│           ├── agents/
│           │   ├── base_agent.py
│           │   ├── business_agent/    ← Agente análisis de negocio
│           │   ├── dev_agent/         ← Agente desarrollo/código
│           │   ├── infra_agent/       ← Agente infraestructura
│           │   └── knowledge_agent/   ← Agente conocimiento fiscal
│           ├── configs/
│           │   ├── agents.yaml        ← Config de agentes
│           │   └── skills.yaml        ← Config de skills
│           ├── memory/
│           │   ├── knowledge_store.py ← Almacén de conocimiento
│           │   ├── qdrant_rag.py      ← RAG + embeddings vía Ollama
│           │   ├── task_history.py    ← Historial de tareas
│           │   └── vector_memory.py   ← Memoria vectorial
│           ├── orchestrator/
│           │   ├── orchestrator.py    ← Coordinador central AI OS
│           │   ├── agent_registry.py  ← Registro de agentes
│           │   ├── skill_registry.py  ← Registro de skills
│           │   └── task_router.py     ← Enrutador de tareas
│           ├── prompts/
│           │   ├── orchestrator_prompt.md
│           │   └── soul.md            ← Identidad/alma del sistema
│           ├── skills/
│           │   ├── base_skill.py
│           │   ├── analysis/skill.py  ← Análisis de datos
│           │   ├── filesystem/skill.py
│           │   ├── github/skill.py
│           │   ├── shell/skill.py
│           │   └── web_search/skill.py
│           └── swarm/
│               └── queen.py           ← Queen-Worker swarm paralelo
│
├── frontend/
│   ├── Dockerfile                     ← Next.js build baked en imagen
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── .env.example
│   └── src/
│       ├── app/
│       │   ├── layout.tsx             ← Root layout
│       │   ├── page.tsx               ← Redirect a /panel/login
│       │   ├── globals.css
│       │   ├── error.tsx
│       │   ├── login/page.tsx         ← Login screen
│       │   ├── forgot-password/page.tsx
│       │   ├── fourgea/usuario/page.tsx ← Portal cliente Fourgea
│       │   └── (app)/                 ← Rutas protegidas (AuthGuard)
│       │       ├── layout.tsx         ← Layout con Sidebar
│       │       ├── dashboard/page.tsx ← KPIs financieros + gráficas
│       │       ├── facturas/page.tsx  ← Gestión CFDI
│       │       ├── cierre/page.tsx    ← Pre-cierre y cierre oficial
│       │       ├── mve/page.tsx       ← Manifestaciones de Valor
│       │       ├── nomina/page.tsx    ← Nómina
│       │       ├── tasks/page.tsx     ← GSD Tareas
│       │       ├── brain/page.tsx     ← Chat Brain IA
│       │       ├── whatsapp/page.tsx  ← QR + estado WA
│       │       ├── telegram/page.tsx  ← Estado bot
│       │       ├── admin/page.tsx     ← Multi-tenant + AI OS status
│       │       ├── billing/page.tsx   ← Planes + Mercado Pago
│       │       ├── contador/page.tsx
│       │       ├── directorio/page.tsx
│       │       └── resico/page.tsx
│       ├── components/
│       │   ├── layout/
│       │   │   ├── AuthGuard.tsx      ← Protección de rutas JWT
│       │   │   └── Sidebar.tsx        ← Navegación lateral
│       │   └── ui/
│       │       ├── Badge.tsx
│       │       ├── BrainWidget.tsx    ← Widget chat IA flotante
│       │       └── Card.tsx
│       └── lib/
│           ├── api.ts                 ← Cliente HTTP para la API
│           └── auth.ts                ← Manejo tokens JWT
│
├── whatsapp/
│   ├── server.js                      ← Microservicio WA (Baileys 6.7.21)
│   ├── package.json
│   └── Dockerfile
│
├── bot/
│   ├── mystic_bot.py                  ← Bot Telegram
│   ├── requirements.txt
│   └── Dockerfile
│
├── infra/
│   ├── docker-compose.vps.yml         ← ⚠️ PRODUCCIÓN (usar en VPS)
│   ├── docker-compose.yml             ← Desarrollo local
│   ├── .env.vps                       ← Template variables entorno
│   ├── database/
│   │   ├── init-schemas.sql           ← Schema inicial
│   │   └── multi-tenant.sql           ← RLS + funciones multi-tenant
│   ├── nginx/
│   │   ├── nginx.conf                 ← Nginx local
│   │   └── nginx-vps.conf             ← Nginx VPS (reverse proxy)
│   └── monitoring/
│       └── prometheus.yml
│
├── .github/
│   └── workflows/
│       ├── deploy.yml                 ← CI/CD: push main → deploy VPS
│       ├── ci.yml                     ← Tests automáticos
│       └── backup.yml                 ← Backup DB programado
│
├── n8n_workflows/
│   ├── alert_manana.json
│   ├── alert_tarde.json
│   └── mapeo_legal.json
│
├── scripts/
│   ├── migrate_legacy.py
│   ├── migrate_mve_v2.py
│   ├── seed_fourgea_docs.py           ← Seed documentos Fourgea → Qdrant
│   ├── seed_knowledge.py
│   ├── seed_legal_mve.py
│   ├── seed_qdrant.py
│   ├── setup_rag.sh
│   └── start_system.sh
│
├── tests/
│   ├── test_api.py
│   └── test_skills.py
│
├── docs/
│   ├── agent_swarm_architecture.md
│   ├── memory_design.md
│   └── system_overview.md
│
├── CLAUDE.md                          ← Instrucciones para Claude Code
├── README.md
└── .gitignore
```

---

## 2. STACK TECNOLÓGICO

### Backend
| Componente | Tecnología | Versión |
|---|---|---|
| Framework API | FastAPI | ≥0.104.0 |
| Runtime | Python | 3.11 |
| ORM | SQLAlchemy | ≥2.0.23 |
| Base de datos | PostgreSQL | 15-alpine |
| Caché | Redis | 7-alpine |
| Auth | JWT (PyJWT) + bcrypt | ≥2.11.0 / ≥4.0.0 |
| HTTP cliente | httpx | ≥0.27.0 |
| Vector DB | Qdrant | ≥1.9.0 |
| LLM local | Ollama (phi3:mini) | latest |
| Embeddings | nomic-embed-text | via Ollama |

### Frontend
| Componente | Tecnología | Versión |
|---|---|---|
| Framework | Next.js | 14.2.3 |
| UI | React | 18.3.1 |
| Lenguaje | TypeScript | 5.4.5 |
| Estilos | TailwindCSS | 3.4.4 |
| Gráficas | Recharts | 2.12.7 |
| Íconos | Lucide React | 0.378.0 |

### Infraestructura
| Componente | Tecnología |
|---|---|
| Contenedores | Docker + Docker Compose v2 |
| Reverse Proxy | Nginx |
| SSL | Let's Encrypt (certbot) |
| CI/CD | GitHub Actions (self-hosted runner en VPS) |
| WhatsApp | Baileys 6.7.21 (Node.js) |
| Bot | python-telegram-bot |
| Automatización | N8N |

---

## 3. ARQUITECTURA DEL SISTEMA

```
Internet
    │
    ▼
Nginx (:80/:443)
    │
    ├── /api/          → mystic_api     :8000  (FastAPI)
    ├── /panel/        → mystic_frontend:3000  (Next.js 14)
    ├── /n8n/          → mystic_n8n     :5679
    ├── /whatsapp/     → mystic_wa      :3001  (Baileys)
    └── /              → web/           (Landing estática)

mystic_api :8000
    │
    ├── PostgreSQL :5432  (mystic_postgres)
    ├── Redis      :6379  (mystic_redis)
    ├── Qdrant     :6333  (mystic_qdrant)  ← RAG + vectores
    └── Ollama     interno (mystic_ollama) ← phi3:mini + nomic-embed-text

mystic_bot (Telegram, polling)
    └── → mystic_api :8000

mystic_wa :3001 (WhatsApp Baileys)
    └── → mystic_api /api/brain/ask (RAG automático por WA)
```

### Red Docker
- **Red interna:** `mystic_net` (bridge)
- **Volúmenes persistentes:** `postgres_data`, `redis_data`, `ollama_data`, `qdrant_data`, `wa_data`, `n8n_data`

---

## 4. MODELOS DE BASE DE DATOS

### Tablas principales (15 modelos SQLAlchemy)

```python
# database.py — Conexión
DATABASE_URL = os.getenv("DATABASE_URL",
    "postgresql://mystic_user:MysticSecure2026!@localhost:5432/mystic_db")
engine = create_engine(DATABASE_URL)

# models.py — Entidades

class Tenant(Base):
    __tablename__ = "tenants"
    id          = Column(String, PK)   # UUID
    nombre      = Column(String)
    rfc         = Column(String)       # RFC SAT México
    direccion   = Column(Text)
    plan        = Column(String)       # basico|business|pro|magia
    activo      = Column(Boolean)
    created_at  = Column(DateTime)

class Usuario(Base):
    __tablename__ = "usuarios"
    id           = Column(String, PK)
    tenant_id    = Column(String, FK→tenants)
    nombre       = Column(String)
    email        = Column(String, unique)
    password_hash= Column(String)      # bcrypt
    rol          = Column(String)      # ceo|contador|admin
    activo       = Column(Boolean)

class Factura(Base):
    __tablename__ = "facturas"
    # CFDI 4.0 — UUID SAT, RFC emisor/receptor, régimen, conceptos, IVA, IEPS
    # Campos: id, tenant_id, uuid_cfdi, fecha, tipo(I/E/T/N/P),
    #         subtotal, iva, total, moneda, tipo_cambio, xml_content, estado

class Empleado(Base):
    __tablename__ = "empleados"
    # NSS, CURP, RFC, salario_diario, tipo_contrato, imss, infonavit
    # Soporta cálculo de nómina ISR tabla 2024, IMSS cuotas

class Nomina(Base):
    __tablename__ = "nomina"
    # empleado_id, periodo(quincenal/mensual), percepciones, deducciones,
    # isr_retenido, imss_empleado, neto

class CierreMes(Base):
    __tablename__ = "cierres_mes"
    # tenant_id, año (con ñ), mes, ingresos, gastos, iva_cobrado,
    # iva_pagado, isr_estimado, estado(borrador|cerrado)

class MVE(Base):
    __tablename__ = "mves"
    # Manifestación de Valor en Exportación — pedimento, RFC, valor_usd,
    # tipo_cambio, incoterm, estado(R/G/C/E), validaciones SAT

class GSDTask(Base):
    __tablename__ = "gsd_tasks"
    # titulo, descripcion, estado, prioridad, asignado_a, vence_en

class BrainSession(Base):
    __tablename__ = "brain_sessions"
    # tenant_id, pregunta, respuesta, modelo, tokens, fuente(rag/llm/rule)

class BrainFeedback(Base):
    __tablename__ = "brain_feedback"
    # session_id, rating(+1/-1), comentario

class Lead(Base):          # CRM básico
class Contacto(Base):      # Directorio
class AlertaConfig(Base):  # Alertas configurables
class AuditLog(Base):      # Registro de acciones por tenant
class AccessLog(Base):     # Log de accesos a la API
class PasswordResetToken(Base):
```

### Multi-tenancy y RLS
```sql
-- Row Level Security activado
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_tenant_isolation ON users
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Función para establecer contexto
CREATE OR REPLACE FUNCTION set_tenant_context(tenant_id UUID)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_tenant_id', tenant_id::text, false);
END;
$$ LANGUAGE plpgsql;
```

### Tenants activos
| Tenant | RFC | Plan | Contacto |
|---|---|---|---|
| Fourgea México SA de CV | FME080820LC2 | business | nathaly@fourgea.mx |
| Triple R Oil México | O150504GE3 | business | admin@tripler.mx |

---

## 5. API ENDPOINTS — CATÁLOGO COMPLETO

### Auth
```
POST /auth/login              → {email, password} → JWT token (30 días)
POST /auth/register           → Crear usuario (admin/ceo)
POST /auth/forgot-password    → Email recuperación
POST /auth/reset-password     → Reset con token
```

### Status
```
GET  /status                  → {api, db, redis, timestamp}
GET  /health                  → 200 OK (Nginx health check)
```

### Facturas / CFDI
```
GET  /facturas                → Lista con filtros (tenant_id JWT)
POST /facturas                → Crear factura manual
POST /facturas/upload-xml     → Parsear CFDI 4.0 XML → guardar
GET  /facturas/{id}           → Detalle
DELETE /facturas/{id}         → Eliminar (solo estado cancelado)
GET  /facturas/estadisticas   → Totales IVA, ISR por período
```

### Empleados y Nómina
```
GET    /empleados             → Lista empleados del tenant
POST   /empleados             → Alta empleado (NSS, CURP, RFC)
GET    /empleados/{id}
PUT    /empleados/{id}
DELETE /empleados/{id}
POST   /nomina/calcular       → Calcular nómina del período
GET    /nomina                → Historial nómina
```

### Cierre de Mes
```
GET  /cierre/{ano}/{mes}              → Pre-cierre en tiempo real (NO guarda)
POST /cierre/{ano}/{mes}/borrador     → Guarda como borrador (editable)
POST /cierre/{ano}/{mes}/guardar      → Cierre oficial (bloqueado)
GET  /cierre/{ano}/{mes}/estado       → Estado del cierre guardado
```
> ⚠️ CRÍTICO: columna `año` (con ñ) — usar `setattr(obj, "año", val)` y `getattr(CierreMes, "año")` en queries

### MVE — Manifestación de Valor en Exportación
```
GET    /mve                   → Lista MVEs con semáforo RGCE
POST   /mve                   → Crear nueva MVE
GET    /mve/{id}
PUT    /mve/{id}
DELETE /mve/{id}
POST   /mve/{id}/validar      → Validar contra reglas SAT
```

### Brain IA
```
POST /api/brain/ask           → RAG + Ollama (Redis→Qdrant→PG→phi3:mini)
POST /api/brain/swarm ★       → Queen-Worker paralelo (3 agentes)
POST /api/brain/feedback ★    → Rating respuesta (+1/-1)
GET  /api/brain/sessions      → Historial de sesiones
```

### AI OS — Orquestador
```
GET  /ai/status               → {agents:[4], skills:[5]}
POST /ai/task                 → Tarea a agente único
POST /ai/swarm                → Tarea a múltiples agentes paralelo
```

### Admin Multi-tenant
```
GET   /admin/tenants                          → Lista tenants con métricas
PATCH /admin/tenants/{id}/plan                → Cambiar plan
GET   /admin/tenants/{id}/cierre/{ano}/{mes}  → Cierre de cualquier tenant
```

### Pagos / Mercado Pago
```
GET  /payments/planes                → Planes y precios MXN
POST /payments/mp/preference         → Crear preferencia MP
POST /payments/mp/webhook            → Webhook MP → actualizar plan
```

### WhatsApp
```
GET  /whatsapp/status         → Estado conexión WA
GET  /whatsapp/qr             → QR base64 para escanear
POST /whatsapp/send           → Enviar mensaje {to, message}
```

### Otros
```
GET  /tipo-cambio             → USD/MXN actualizado
GET  /dashboard               → KPIs consolidados del tenant
POST /leads                   → Crear lead CRM
GET  /leads                   → Lista leads
GET  /contactos               → Directorio
```

---

## 6. AI OS — ARQUITECTURA DE AGENTES

```
AI OS v2.0 — Basado en: FastAPI + Ollama + Qdrant + Redis

Orchestrator (orchestrator.py)
    │
    ├── AgentRegistry      ← Registro de agentes disponibles
    ├── SkillRegistry      ← Registro de skills disponibles
    ├── TaskRouter         ← Enruta tareas al agente correcto
    ├── TaskHistory        ← Persiste historial en .data/tasks.json
    └── KnowledgeStore     ← Base de conocimiento en .data/knowledge.json

Agentes (4 activos):
    ├── business_agent     ← Análisis negocio, KPIs, reportes
    ├── dev_agent          ← Generación/revisión de código
    ├── infra_agent        ← Docker, servidores, deployments
    └── knowledge_agent    ← Consultas legales, fiscales, docs

Skills (5 activos):
    ├── web_search         ← DuckDuckGo search
    ├── analysis           ← Análisis estadístico
    ├── filesystem         ← Lectura/escritura archivos
    ├── github             ← Operaciones Git/GitHub
    └── shell              ← Comandos shell
```

### Queen-Worker Swarm (queen.py)
```
Pregunta compleja
    │
    ▼
QueenAgent._route()
    │ ← Analiza keywords para detectar área
    ├── AgentFacturas  (keywords: factura, cfdi, ingreso, egreso...)
    ├── AgentNomina    (keywords: nómina, sueldo, IMSS, INFONAVIT...)
    └── AgentIVA       (keywords: IVA, DIOT, acreditamiento, tasa...)
            │
            ▼ asyncio.gather() — ejecución PARALELA
            │
    QueenAgent._consolidate()
            │
            ▼
    Respuesta consolidada
```

### RAG Pipeline (qdrant_rag.py)
```
Pregunta → nomic-embed-text (Ollama local) → vector 768 dims
         → Qdrant cosine similarity search (threshold 0.5)
         → Top-K chunks relevantes
         → Contexto + prompt → phi3:mini (Ollama)
         → Respuesta

Colecciones Qdrant:
    ├── fiscal_mx          ← Leyes SAT, LIVA, LISR
    ├── fourgea_docs       ← Documentos específicos Fourgea
    └── knowledge_base     ← Conocimiento general del sistema
```

### Filosofía de Costos (soul.md)
```
Nivel 0 — Determinístico ($0):  reglas, cálculos, lookups BD
Nivel 1 — Caché RAG ($0):       contexto en memoria vectorial
Nivel 2 — Ollama local ($0):    phi3:mini en hardware propio
Nivel 3 — Claude API (5%):      solo cuando niveles 0-2 no alcanzan

Objetivo: >75% queries sin llamada LLM en el mes 6.
```

---

## 7. SEGURIDAD

```python
# security.py

# JWT
SECRET_KEY    = env("SECRET_KEY")       # HS256
TOKEN_EXPIRE  = 30 días
SYSTEM_TOKEN  = env("SYSTEM_TOKEN")     # Para N8N y apps internas

# Contraseñas
bcrypt.hashpw() / bcrypt.checkpw()

# Roles
ceo      → acceso total + admin tenants
admin    → gestión usuarios + admin tenants
contador → solo su tenant

# CORS
allow_origins = env("CORS_ORIGINS", "*")  # Restringir en producción
```

### Variables de entorno requeridas (infra/.env.vps)
```bash
POSTGRES_USER=        # Usuario PostgreSQL
POSTGRES_PASSWORD=    # Password PostgreSQL
POSTGRES_DB=          # Nombre base de datos
REDIS_PASSWORD=       # Password Redis
SECRET_KEY=           # Clave JWT HS256 (mínimo 32 chars)
TELEGRAM_TOKEN=       # Token del bot de Telegram
N8N_USER=             # Usuario N8N
N8N_PASSWORD=         # Password N8N
DOMAIN=               # sonoradigitalcorp.com
CORS_ORIGINS=         # https://sonoradigitalcorp.com

# Pendientes agregar:
MP_ACCESS_TOKEN=      # Mercado Pago (pendiente Marco)
WA_API_KEY=           # MysticWA2026! (ya configurado)
SYSTEM_TOKEN=         # Token interno para N8N→API
OLLAMA_URL=           # http://ollama:11434
QDRANT_URL=           # http://qdrant:6333
```

---

## 8. INFRAESTRUCTURA — DOCKER COMPOSE VPS

### Contenedores activos (9 total)
```yaml
# infra/docker-compose.vps.yml

services:
  postgres:     image: postgres:15-alpine   | port: 5432 | volume: postgres_data
  redis:        image: redis:7-alpine       | port: 6379 | volume: redis_data
  ollama:       image: ollama/ollama        | interno    | volume: ollama_data
  qdrant:       image: qdrant/qdrant        | port: 6333 | volume: qdrant_data
  api:          build: ./backend            | port: 8000 | healthcheck: /status
  frontend:     build: ./frontend           | port: 3000 | NEXT_PUBLIC_API_URL
  bot:          build: ./bot                | interno    | TELEGRAM_TOKEN
  whatsapp:     build: ./whatsapp           | port: 3001 | WA_API_KEY
  n8n:          image: n8nio/n8n            | port: 5679 | volume: n8n_data
  nginx:        image: nginx:alpine         | port: 80/443
```

### Red
```
mystic_net (bridge interno)
    ├── api ←→ postgres, redis, qdrant, ollama
    ├── frontend ←→ nginx
    ├── bot ←→ api
    ├── whatsapp ←→ api
    └── nginx ←→ api, frontend, n8n, whatsapp
```

### Comandos críticos de operación
```bash
# Desde /home/mystic/sonora-digital-corp/infra/

# Levantar todo
docker compose -f docker-compose.vps.yml --env-file .env up -d

# Rebuild API (rápido, sin rebuild de imagen)
docker cp main.py mystic_api:/app/main.py && docker restart mystic_api

# Rebuild frontend (REQUIERE Python subprocess por ! en passwords)
python3 -c "
import subprocess, os
subprocess.run(
    ['docker','compose','-f','docker-compose.vps.yml','build','frontend','--no-cache'],
    cwd='/home/mystic/sonora-digital-corp/infra',
    env={**os.environ,'NEXT_PUBLIC_API_URL':'https://sonoradigitalcorp.com/api'}
)
"

# Logs en tiempo real
docker logs -f mystic_api
docker logs -f mystic_wa
docker logs -f mystic_bot

# Verificar salud
curl http://localhost:8000/status

# Modelos Ollama disponibles
docker exec mystic_ollama ollama list
# Activo: phi3:mini
# Pendiente: docker exec mystic_ollama ollama pull deepseek-r1:1.5b
```

---

## 9. CI/CD — GITHUB ACTIONS

### Deploy (.github/workflows/deploy.yml)
```
Trigger: push a main (o workflow_dispatch)
Runner: self-hosted (VPS Hostinger)

Pasos:
1. git fetch + reset --hard origin/main
2. docker compose build api --no-cache → up -d api
3. Si cambió frontend/ → build frontend → up -d frontend
4. Si cambió bot/ → build bot → up -d bot
5. Health check: GET http://localhost:8000/status → assert "api":"ok"
6. Notificación Telegram (✅/❌)

Secrets requeridos:
  TELEGRAM_TOKEN    → notificaciones deploy
  TELEGRAM_CHAT_ID  → chat de Marco
```

### CI Tests (.github/workflows/ci.yml)
```
Trigger: push main/develop + PRs a main
Runner: ubuntu-latest (GitHub hosted)

Servicios: postgres:15 + redis:7 (ephemeros)

Pasos:
1. Setup Python 3.11
2. pip install requirements.txt + pytest
3. python -c "Base.metadata.create_all() → 'DB OK'"
4. pytest tests/ -v --tb=short
5. python -c "import main → 'Imports OK'"
```

### Backup (.github/workflows/backup.yml)
- Backup programado de base de datos

---

## 10. NGINX — CONFIGURACIÓN VPS

```nginx
# infra/nginx/nginx-vps.conf

server {
    listen 80;
    server_name sonoradigitalcorp.com;
    client_max_body_size 20M;

    # API Backend
    location /api/ {
        proxy_pass http://api:8000/;
        proxy_read_timeout 120s;
    }

    # API Docs
    location /docs   { proxy_pass http://api:8000/docs; }
    location /redoc  { proxy_pass http://api:8000/redoc; }

    # N8N (WebSocket habilitado)
    location /n8n/ {
        proxy_pass http://n8n:5678/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Dashboard Next.js
    location /panel/ {
        proxy_pass http://frontend:3000/;
    }

    # WhatsApp microservicio
    location /whatsapp/ {
        proxy_pass http://whatsapp:3001/;
    }

    # Health check
    location /health { return 200 "ok\n"; }

    # Landing estática
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

> SSL: Let's Encrypt via certbot. Agregar bloque HTTPS con ssl_certificate cuando se renueve.

---

## 11. WHATSAPP — MICROSERVICIO (Baileys 6.7.21)

```javascript
// whatsapp/server.js

// Config
PORT      = 3001
API_KEY   = WA_API_KEY || 'MysticWA2026!'
AUTH_DIR  = /wa-data/auth     ← sesión persistente en volumen Docker

// Endpoints
GET  /status     → {state: connected|qr|disconnected, number}
GET  /qr         → {qr: "data:image/png;base64,..."} ← escanear desde panel
POST /send       → {to: "521XXXXXXXXXX@s.whatsapp.net", message: "..."}

// Flujo mensajes entrantes
sock.ev.on('messages.upsert') →
    filtrar grupos (@g.us, @lid) →
    ignorar propios mensajes →
    POST a WEBHOOK_URL (mystic_api /brain/ask) →
    responder vía sock.sendMessage()

// Número actual: 6623538272 (Marco — temporal)
// Whitelist: 6622681111 (Nathaly), 6623538272 (Marco)
// Pendiente: chip prepago Telcel dedicado (~$50 MXN)
```

---

## 12. TELEGRAM BOT

```python
# bot/mystic_bot.py

# Comandos disponibles
/start      → Menú principal con botones inline
/status     → Estado API (✅/❌ api, db, redis)
/dashboard  → KPIs financieros del tenant (requiere login)
/login      → Autenticación via email+password
/cierre     → Estado cierre del mes actual
/facturas   → Últimas 5 facturas
/help       → Lista de comandos

# Auth flow
/login email password → POST /auth/login → guarda JWT en memoria
Token se usa en todas las peticiones siguientes

# Usuarios permitidos
ALLOWED_USERS = env("ALLOWED_USERS")  # IDs Telegram separados por coma
```

---

## 13. CÁLCULOS FISCALES — 147 FUNCIONES (calculos_completos_147.py)

### Categorías principales
```python
class CalculosCompletos147:

    # Utilidades
    iva_basico(subtotal, tasa=0.16)
    utilidad_bruta(ingresos, costo)
    utilidad_operativa(bruta, gastos)
    utilidad_neta(operativa, impuestos)
    isr_base(utilidad, tasa=0.30)
    ptu(utilidad, tasa=0.10)
    margen_neto(utilidad_neta, ingresos)
    roa(utilidad_neta, activos)
    roe(utilidad_neta, patrimonio)
    ebitda(neta, impuestos, intereses, deprec, amort)

    # Cierre maestro
    generar_cierre_maestro(datos: dict) → {
        ingresos, costo_ventas, utilidad_bruta,
        margen_bruto_pct, gastos_operativos, utilidad_operativa,
        isr_estimado, ptu_estimada, utilidad_neta,
        margen_neto_pct, iva_cobrado, ebitda
    }

    # + ~137 funciones más:
    # Nómina ISR tabla 2024, IMSS cuotas, INFONAVIT
    # IVA acreditable, DIOT, prorrateo
    # Importación/exportación (pedimentos, valoración aduanera)
    # RESICO cálculos simplificados
    # Tipo de cambio, conversiones USD/MXN
    # Razones financieras (liquidez, solvencia, rotación)
    # Declaraciones mensuales/anuales estimadas
```

---

## 14. FRONTEND — PÁGINAS Y COMPONENTES

### Rutas y descripción
```
/panel/login              → Auth screen (email + password)
/panel/forgot-password    → Recuperación contraseña
/panel/dashboard          → KPIs: ingresos, gastos, IVA, facturas recientes + gráficas Recharts
/panel/facturas           → CRUD facturas + upload XML CFDI
/panel/cierre             → Flujo: pre-cierre → borrador → cerrado
/panel/mve                → Manifestaciones de Valor con semáforo (R/G/C/E)
/panel/nomina             → Nómina empleados
/panel/tasks              → GSD Tareas
/panel/brain              → Chat Brain IA (RAG + Ollama)
/panel/whatsapp           → Estado WA + QR escaneo
/panel/telegram           → Estado bot
/panel/admin              → Multi-tenant (solo admin/ceo) + AI OS status
/panel/billing            → Planes ($499/$999/$1999/$3999) + MP integration
/panel/contador           → Vista contador
/panel/directorio         → CRM contactos
/panel/resico             → Cálculos RESICO
/fourgea/usuario          → Portal cliente Fourgea (sin sidebar)
```

### Componentes reutilizables
```typescript
// AuthGuard.tsx — Protege todas las rutas (app)/
// Lee JWT de localStorage, valida expiración, redirect /panel/login

// Sidebar.tsx — Navegación lateral con íconos Lucide
// Roles: admin/ceo ven Admin + Billing; contador ve vista reducida

// BrainWidget.tsx — Chat flotante IA disponible en todas las páginas
// POST /api/brain/ask → streaming response

// Card.tsx, Badge.tsx — UI primitives Tailwind

// lib/api.ts — fetch wrapper con JWT auto-inject
// lib/auth.ts — login/logout/getUser helpers
```

### Variables de entorno frontend
```bash
NEXT_PUBLIC_API_URL=https://sonoradigitalcorp.com/api
# ⚠️ Baked en imagen al hacer docker build
# Para cambiar: rebuild completo del frontend
```

---

## 15. N8N — WORKFLOWS

```
Endpoint:  https://sonoradigitalcorp.com/n8n
Auth:      API Key — mystic_n8n_0a581672f5e34a88a74ab054b9f1242e
           (UI de login roto — usar solo API key)

Workflows en disco:
├── alert_manana.json   ← Alerta matutina estado del sistema
├── alert_tarde.json    ← Alerta vespertina
└── mapeo_legal.json    ← Automatización mapeo legal MVE

Webhooks:
  Mystic API → N8N: POST /n8n/webhook/{id}
  N8N → Mystic API: Bearer SYSTEM_TOKEN
```

---

## 16. PLANES Y PRECIOS

```
Plan      Precio MXN/mes    Características
─────────────────────────────────────────────
Básico    $499              Facturas + Nómina básica
Business  $999              + Cierre mes + MVE + Brain IA básico
Pro       $1,999            + AI OS + WhatsApp + multi-usuario
Magia     $3,999            + N8N workflows + soporte dedicado

Pago: Mercado Pago
  POST /payments/mp/preference → redirect MP → webhook → plan actualizado
  Pendiente: MP_ACCESS_TOKEN (Marco compartirá desde WA)
```

---

## 17. DATOS REALES — CLIENTE FOURGEA

```
Razón social: Fourgea Mexico SA de CV
RFC:          FME080820LC2
Giro:         Filtración de fluidos industriales (importador)
Empleados:    12
Pedimento:    26-23-3680-6000156

Usuarios activos:
  nathaly@fourgea.mx / Nathaly2026!  → rol: contador
  marco@fourgea.mx   / Marco2026!    → rol: ceo

WhatsApp activo:
  6622681111 (Nathaly) → whitelist → respuestas automáticas Brain IA
  Contexto automático: "fourgea" → preguntas sobre su empresa

Pendiente:
  → Cargar XMLs/CFDIs históricos → cierre de mes real
  → Seed documentos específicos Fourgea → Qdrant
```

---

## 18. PENDIENTES Y DEUDA TÉCNICA

### Alta prioridad
- [ ] `MP_ACCESS_TOKEN` → agregar a docker-compose.vps.yml (Marco da link desde WA)
- [ ] Pull `deepseek-r1:1.5b` en Ollama (actualmente solo phi3:mini)
- [ ] Cargar XMLs/CFDIs reales de Fourgea → cierre de mes real

### Media prioridad
- [ ] Chip prepago Telcel (~$50 MXN) → número WhatsApp dedicado para Mystic
- [ ] Seed Qdrant con más docs de Fourgea
- [ ] N8N workflows activos (actualmente en draft)
- [ ] Tests unitarios (tests/ casi vacío)

### Mejoras arquitectónicas
- [ ] Alembic migrations (actualmente `Base.metadata.create_all()` directo)
- [ ] CORS restringido (actualmente `"*"` en producción)
- [ ] Rate limiting en endpoints Brain IA (puede ser costoso en Ollama)
- [ ] Monitoreo con Prometheus/Grafana (prometheus.yml existe pero inactivo)
- [ ] LLM Arena: multi-LLM (Gemini/Grok/GPT/Qwen) comparativo en ramas Git

---

## 19. COMANDOS DE REFERENCIA RÁPIDA

```bash
# ── SISTEMA ──
docker ps                                          # Ver contenedores
docker logs -f mystic_api --tail=50                # Logs API
docker exec -it mystic_postgres psql -U mystic_user mystic_db  # PostgreSQL CLI
docker exec -it mystic_redis redis-cli             # Redis CLI

# ── DEPLOY MANUAL ──
cd /home/mystic/sonora-digital-corp
git pull origin main
cd infra
docker compose -f docker-compose.vps.yml --env-file .env up -d --build api

# ── API TEST ──
curl http://localhost:8000/status
curl http://localhost:8000/docs   # Swagger UI

# ── GIT ──
git -C /home/mystic/sonora-digital-corp status
git -C /home/mystic/sonora-digital-corp log --oneline -10

# ── OLLAMA ──
docker exec mystic_ollama ollama list
docker exec mystic_ollama ollama pull deepseek-r1:1.5b   # PENDIENTE
docker exec mystic_ollama ollama pull nomic-embed-text    # Para RAG

# ── QDRANT ──
curl http://localhost:6333/collections              # Listar colecciones

# ── WA QR ──
curl "http://localhost:3001/qr" -H "x-api-key: MysticWA2026!"
# O desde browser: https://sonoradigitalcorp.com/whatsapp/qr?apikey=MysticWA2026%21

# ── N8N ──
curl -H "X-N8N-API-KEY: mystic_n8n_0a581672f5e34a88a74ab054b9f1242e" \
     http://localhost:5679/api/v1/workflows
```

---

## 20. DIAGRAMA DE FLUJO — MENSAJE WHATSAPP ENTRANTE

```
Nathaly envía WA: "¿Cuánto IVA pagué en febrero?"
    │
    ▼
mystic-wa (Baileys) recibe mensaje
    │ verifica whitelist → 6622681111 ✓
    ▼
POST http://mystic_api:8000/api/brain/ask
    { "question": "¿Cuánto IVA pagué en febrero?",
      "context": "fourgea",
      "phone": "6622681111" }
    │
    ▼
Brain IA Pipeline:
    1. Redis cache → ¿pregunta reciente? → no
    2. Qdrant RAG  → nomic-embed-text → buscar docs fourgea
    3. PostgreSQL  → facturas febrero Fourgea → calcular IVA
    4. phi3:mini   → generar respuesta contextual
    │
    ▼
Respuesta: "En febrero 2026 el IVA trasladado fue de $X,XXX MXN..."
    │
    ▼
mystic-wa envía respuesta a Nathaly por WA ✓
    │
    ▼
BrainSession guardada en PostgreSQL (para historial + feedback)
```

---

> **Generado:** 19 Marzo 2026
> **Por:** MYSTIC AI OS v2.2 — Claude Code (Sonnet 4.6)
> **Para:** Revisión Ingeniero de Sistemas
> **Backup anterior:** /home/mystic/MYSTIC_BLUEPRINT.md.bak
