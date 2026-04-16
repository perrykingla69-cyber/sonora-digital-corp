# FASE 1 — SaaS Backbone Sonora Digital Corp

## Resumen

Implementación completa del backbone SaaS: Dashboard + Auth API + Agent Factory + Bot Factory.

## Qué se construyó

### 1. SaaS Dashboard (`apps/dashboard/`)
- Next.js 14 + TypeScript + Tailwind + Framer Motion
- `/auth/signup` — Registro con auto-creación de tenant
- `/auth/login` — Login JWT
- `/dashboard` — Home con stats y quick actions
- `/dashboard/automation` — Formulario crear agente
- `/dashboard/bots` — Tabla de bots con auto-refresh
- `/dashboard/settings` — API keys + perfil + suscripción
- `/pricing` — Tabla de planes Free/Pro/Enterprise
- Puerto: 3001

### 2. User Management API (`apps/api/app/api/v1/signup.py`)
Nuevos endpoints en hermes-api:
- `POST /api/v1/users/signup` — Registro + auto-tenant + JWT
- `POST /api/v1/users/login` — Login (sin tenant_slug requerido)
- `GET /api/v1/users/me` — Perfil + subs + bots
- `GET /api/v1/users/me/api-keys` — API keys del usuario
- `POST /api/v1/users/me/regenerate-api-key` — Regenerar key

### 3. Agent Deployments API (`apps/api/app/api/v1/agent_deployments.py`)
- `POST /api/v1/agents/create` — Crea agente (async, dispara factory)
- `GET /api/v1/agents/{id}/status` — Estado + progreso del agente
- `GET /api/v1/agents/` — Lista todos los agentes del usuario
- `DELETE /api/v1/agents/{id}` — Eliminar agente

### 4. Bot Factory API (`apps/api/app/api/v1/bots.py`)
- `POST /api/v1/bots/create` — Crea bot para un agente
- `GET /api/v1/bots/{id}/health` — Health check del bot
- `GET /api/v1/bots/` — Lista bots del usuario
- `DELETE /api/v1/bots/{id}` — Eliminar bot

### 5. Agent Factory Service (`apps/agent-factory/`)
- FastAPI independiente en puerto 8001 (interno)
- Selección automática de modelo: Gemini Flash (simple) vs Claude (complejo)
- Build Docker automático del agente
- Deploy como container en la red hermes_network
- 4 templates: `chat`, `task`, `data-processor`, `webhook`

### 6. Bot Factory en ClawBot (`apps/clawbot/bot-factory.js`)
- `POST /api/v1/bots/register` — Registro interno de bots
- `POST /api/v1/bots/:id/set-token` — Activar con token Telegram
- `POST /webhook/telegram/:bot_id` — Recibe mensajes del usuario
- Dedup con Redis + cifrado AES-256 para tokens

### 7. DB Migration (`infra/migrations/004_saas_tables.sql`)
Tablas nuevas:
- `plans` — Free/Pro/Enterprise con precios y límites
- `subscriptions` — Suscripciones por usuario/tenant
- `agent_deployments` — Registro de agentes desplegados
- `bots` — Bots conectados a agentes
- Columnas nuevas en `users`: `company_name`, `subscription_plan`, `api_key`, etc.

## Deploy en VPS

### 1. Ejecutar migración
```bash
ssh vps
cd /home/mystic/hermes-os
git pull origin main

# Ejecutar migración
docker compose -f infra/docker-compose.yml exec -T postgres \
  psql -U mystic -d mystic_unified < infra/migrations/004_saas_tables.sql

# O usando el script:
bash infra/scripts/run-migration.sh 004_saas_tables.sql
```

### 2. Levantar nuevos servicios
```bash
cd /home/mystic/hermes-os/infra
docker compose up -d dashboard agent-factory
docker compose ps
```

### 3. Verificar servicios
```bash
# Dashboard
curl http://localhost:3001/api/health  # debe responder

# Agent Factory
curl http://agent-factory:8000/health  # desde red interna

# Hermes API nuevos endpoints
curl -X POST http://localhost:8000/api/v1/users/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test1234","full_name":"Test","company_name":"Test Corp"}'
```

### 4. Variables de entorno requeridas
Agregar a `/home/mystic/hermes-os/infra/.env`:
```bash
AGENT_FACTORY_URL=http://agent-factory:8000
NEXT_PUBLIC_API_URL=https://sonoradigitalcorp.com/api
AGENT_FACTORY_MAX_CONCURRENT=5
INTERNAL_SECRET=<random-secret>
GOOGLE_API_KEY=<your-google-key>
```

### 5. Nginx — agregar rutas (opcional)
Agregar al nginx.conf para exponer dashboard en subdomain:
```nginx
# dashboard.sonoradigitalcorp.com
server {
    listen 443 ssl;
    server_name dashboard.sonoradigitalcorp.com;
    location / {
        proxy_pass http://hermes_dashboard:3001;
        proxy_set_header Host $host;
    }
}
```

## Estructura de archivos creados

```
apps/
  dashboard/           — Next.js 14 SaaS Dashboard
    app/auth/signup/   — Registro
    app/auth/login/    — Login
    app/dashboard/     — Home, Automation, Bots, Settings
    app/pricing/       — Planes
    components/        — AuthLayout, DashboardLayout, AutomationForm, BotTable, PricingTable
    lib/api.ts         — API client + JWT helpers

  api/app/api/v1/
    signup.py          — Users: /signup, /login, /me, /api-keys
    agent_deployments.py — Agents CRUD + factory trigger
    bots.py            — Bot factory endpoints

  agent-factory/       — FastAPI service para crear containers
    main.py
    factory.py         — Lógica deploy + templates
    Dockerfile

  clawbot/
    bot-factory.js     — Bot Factory endpoints REST

agents/factories/      — Templates de agentes IA
  chat-agent.template.py
  task-agent.template.py
  data-processor.template.py
  webhook-agent.template.py

infra/
  docker-compose.yml   — Actualizado: dashboard + agent-factory
  migrations/004_saas_tables.sql
  scripts/
    run-migration.sh
    deploy-agent.sh
```

## Límites de planes

| Plan | Agentes | Mensajes/mes | Precio |
|------|---------|--------------|--------|
| Free | 1 | 100 | $0 |
| Pro | 5 | 5,000 | $499 MXN |
| Enterprise | Ilimitado | Ilimitado | $1,999 MXN |

## Selección de modelo por agente

| Tipo | Verticales | Modelo |
|------|-----------|--------|
| chat, webhook | restaurante, tienda... | Gemini Flash (gratis) |
| task, data-processor | contador, abogado | Claude 3.5 Haiku |

## Siguiente paso: Fase 2

- Integración Stripe (pagos en línea)
- Portal de cliente con embed del bot
- Analytics por agente (mensajes, conversiones)
- WhatsApp bot conectado via Evolution API
- Email transaccional (onboarding, alertas)
