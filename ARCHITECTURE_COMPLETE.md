# 🏗️ HERMES OS — ARQUITECTURA COMPLETA

## Overview Visual

```
┌──────────────────────────────────────────────────────────────────┐
│                    SONORA DIGITAL CORP                           │
│           https://sonoradigitalcorp.com (Vercel + VPS)          │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PRESENTATION LAYER (Vercel + Browser)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Mission Control Dashboard                                      │
│  ├─ StatusBoard (Docker, API, DB, Redis health)               │
│  ├─ LogsViewer (real-time SSE streaming)                      │
│  ├─ TasksPanel (Claude Code tasks #1-#3)                      │
│  ├─ AgentsMonitor (HERMES, MYSTIC, ClawBot, CodeAgent)        │
│  ├─ MCPsStatus (GitHub, HuggingFace, OpenRouter, Qdrant)      │
│  └─ CrawbotBridge (Telegram command executor)                 │
│                                                                 │
│  Dashboard Cliente                                              │
│  ├─ Tenant stats (users, storage, API calls)                  │
│  ├─ Chat con HERMES IA                                        │
│  ├─ Alerts + Recommendations                                  │
│  └─ Document library                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (HTTPS)
┌─────────────────────────────────────────────────────────────────┐
│ APPLICATION LAYER (API + Services)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FastAPI (hermes-api:8000)                                      │
│  ├─ POST /api/v1/agents/hermes/chat                           │
│  │  └─ OpenRouter (Gemini) + RAG (Qdrant) + Mock fallback     │
│  ├─ GET /api/v1/agents/mystic/analyze                         │
│  │  └─ Análisis + Alerts + Recommendations                    │
│  ├─ GET /api/v1/agents/status                                 │
│  ├─ GET /api/v1/health                                        │
│  └─ OpenAPI docs: /docs                                       │
│                                                                 │
│  Orchestrator Service (Python)                                  │
│  ├─ Redis listener (eventos de ClawBot)                       │
│  ├─ Agent spawner (docker run con timeout)                    │
│  ├─ Heartbeat monitor (cada 30s)                              │
│  ├─ Kill logic (TTL, RAM threshold, manual)                   │
│  └─ Logging → Mission Control WebSocket                       │
│                                                                 │
│  ClawBot Gateway (Telegram/WhatsApp)                            │
│  ├─ /task [descripción]   → Spawn agent                       │
│  ├─ /orchestrator status  → Ver agents activos                │
│  ├─ /n8n list             → Ver workflows N8N                 │
│  ├─ /n8n run [id]         → Ejecutar workflow                 │
│  └─ /deploy               → Dispara CI/CD                     │
│                                                                 │
│  N8N (Automation Workflows)                                     │
│  ├─ every-6h-scan-tenants (6am, 12pm, 6pm, 12am)             │
│  ├─ on-new-tenant-webhook (trigger: HTTP POST)                │
│  └─ daily-alerts-compile (6am)                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (gRPC/HTTP)
┌─────────────────────────────────────────────────────────────────┐
│ DATA LAYER (Storage + Cache)                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PostgreSQL (hermes_db + evolution_db)                         │
│  ├─ RLS: SET LOCAL app.current_tenant_id (transaction-scoped) │
│  ├─ Tables: usuarios, tenants, invoices, messages, etc        │
│  └─ Migrations: 005_demo_users.sql                            │
│                                                                 │
│  Redis (Cache + Queue)                                          │
│  ├─ Cache: API responses (TTL 1h)                             │
│  ├─ Queue: events (ClawBot → Orchestrator)                    │
│  ├─ Heartbeat: agent uptime tracking                          │
│  └─ Revocation: JWT JTI invalidation                          │
│                                                                 │
│  Qdrant (Vector DB + RAG)                                       │
│  ├─ Collections: tenant_documents, fiscal_docs, recipes       │
│  ├─ Embeddings: nomic-embed-text (768-dim)                    │
│  ├─ Search: Dense (HNSW) + Sparse (BM25) hybrid               │
│  └─ Auto-seed: on new tenant registration                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ EXTERNAL INTEGRATIONS                                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ OpenRouter API (Gemini Flash + GLM Z1)                          │
│ Telegram Bots (HERMES CEO, HERMES Public, MYSTIC, ClawBot)    │
│ WhatsApp (Evolution API)                                       │
│ GitHub Actions (CI/CD auto-deploy)                            │
│ Vercel (Frontend hosting)                                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow — 5 Escenarios Clave

### Scenario 1: CEO ejecuta /task desde Telegram

```
1. CEO: /task "analiza rentabilidad restaurante 1"
   ↓
2. ClawBot valida + publica evento en Redis
   event = {user: 5738935134, task: "...", type: "MYSTIC"}
   ↓
3. Orchestrator escucha Redis, ve evento
   ↓
4. Orchestrator spawn: docker run mysti-agent:latest
   env: TASK_ID=xyz, TENANT_ID=abc, RAM_LIMIT=512M, TIMEOUT=5m
   ↓
5. MYSTIC agent ejecuta (OpenCode en VPS)
   - Lee histórico tenant (PostgreSQL)
   - Genera análisis + alertas
   - Cache en Redis
   ↓
6. MYSTIC termina, retorna: {status: "OK", result: "..."}
   ↓
7. Orchestrator recibe OK
   - Mata proceso (docker kill)
   - Publica resultado en Redis
   - Log en Mission Control WebSocket
   ↓
8. ClawBot recibe resultado en Redis
   - Envía respuesta al CEO en Telegram
   - CEO ve en Mission Control también
   ↓
9. Agente MUERE (no infinito)
   - RAM liberada
   - Listo para siguiente task
```

### Scenario 2: N8N Workflow automático (6am scan)

```
1. Cron trigger: 6am UTC (exactamente una vez)
   ↓
2. N8N inicia workflow "every-6h-scan-tenants"
   ↓
3. Workflow pasos:
   - GET /api/v1/tenants (FastAPI)
   - Para cada tenant:
     - Check health (API calls, storage, users)
     - Detecta anomalías
     - Genera resumen
   ↓
4. Si OK: Webhook payload → ClawBot
   ↓
5. ClawBot publica resumen:
   - Telegram CEO: "✅ 6am scan OK | 12 tenants healthy"
   - Mission Control: log en LogsViewer
   ↓
6. N8N workflow termina
   - No sigue corriendo (no infinito)
   - Próximo trigger: 12pm
```

### Scenario 3: Nuevo tenant se registra

```
1. Usuario regista empresa en signup form
   ↓
2. FastAPI crea tenant en PostgreSQL
   ↓
3. FastAPI publica webhook a N8N
   {event: "tenant.created", tenant_id: "xyz", niche: "restaurante"}
   ↓
4. N8N dispara workflow "on-new-tenant-webhook"
   ↓
5. Workflow:
   - Classify niche (GPT)
   - Seed Qdrant (fetch docs, embed, upsert)
   - Create RAG collections
   - Create demo templates
   ↓
6. N8N termina (una sola ejecución)
   ↓
7. Telegram notif: "Nuevo tenant: Restaurante El Faro ✅ Qdrant listo"
   ↓
8. Usuario puede hacer queries a HERMES ahora
```

### Scenario 4: GitHub push → Auto-deploy

```
1. Commit + git push origin main
   ↓
2. GitHub Actions dispara workflow .github/workflows/deploy.yml
   ↓
3. Jobs en paralelo:
   
   Job A: Deploy Vercel (mission-control)
   - git checkout, npm install, npm build
   - vercel deploy --prod
   - Health: curl -f https://mission-control.vercel.app
   - ~2 min
   
   Job B: Deploy VPS (hermes-api)
   - SSH al VPS
   - git pull, docker compose up -d --build --no-deps hermes-api
   - Health: curl -f http://localhost:8000/health (3x retry)
   - ~3 min
   
   Job C: Notify (after A + B)
   - Si OK: Telegram "✅ Deploy SUCCESS | Vercel: OK | VPS: OK"
   - Si fail: Telegram "❌ Deploy FAILED | See Actions"
   ↓
4. Ambas terminan
   ↓
5. CEO recibe Telegram notif
   - Verifica Mission Control en vivo
   - API responde con datos reales
```

### Scenario 5: Mission Control actualiza en vivo

```
1. CEO abre https://sonoradigitalcorp.com/mission-control/
   ↓
2. Frontend conecta a API via WebSocket (SSE fallback)
   ↓
3. Components subscriben a eventos:
   - StatusBoard: cada 30s GET /api/v1/status (docker ps, RAM, CPU)
   - LogsViewer: SSE GET /api/v1/logs/stream (tail -f)
   - TasksPanel: cada 30s GET /api/v1/tasks (Claude Code tasks)
   - AgentsMonitor: cada 30s GET /api/v1/agents/status
   ↓
4. Backend responde:
   - Si agent levantado: real data
   - Si no: mock data (graceful degradation)
   ↓
5. Frontend renderiza:
   - Cards con animaciones GSAP count-ups
   - Logs scrollean en vivo
   - Alerts se colorean según severidad
   ↓
6. CEO ve TODO: sistema vivo, agents activos, logs en vivo
```

---

## 🎯 Agent Lifecycle Management

```
STATE MACHINE:

IDLE (no task)
  ├─ RAM: ~50MB (parado)
  ├─ CPU: 0%
  └─ $: ~$0 (no costo)
       ↓
    SPAWN (ClawBot: /task)
       ↓
RUNNING (ejecutando tarea)
  ├─ RAM: ~300MB (máx 512MB limit)
  ├─ CPU: ~80%
  ├─ Heartbeat: cada 30s (Redis ping)
  └─ TTL: 5 minutos max (timeout)
       ↓
  [Tarea completa]
       ↓
TERMINATING (limpieza)
  ├─ Flush logs
  ├─ Cache resultado en Redis
  ├─ Notifica ClawBot
       ↓
DEAD (docker kill)
  ├─ RAM: liberada
  ├─ CPU: liberada
  └─ Listo para siguiente task
```

**Protecciones**:
- ⏱️ TTL: Si agent no termina en 5min → kill forzoso
- 💾 RAM: Si >80% usado → matar agentes no-críticos
- 💓 Heartbeat: Si no responde en 30s × 3 → kill
- 🔄 No loops: Agent termina OR muere, nunca infinito

---

## 📡 Integración ClawBot

ClawBot es el **control center** de Luis Daniel:

```
Commands Disponibles:
│
├─ /task [descripción]
│  └─ Spawn HERMES/MYSTIC/CodeAgent, ejecuta, retorna resultado
│
├─ /orchestrator status
│  ├─ Agents en ejecución (name, RAM, uptime)
│  ├─ Queue pending (qué tasks esperan)
│  └─ Health: Vercel OK / VPS OK / Postgres OK
│
├─ /orchestrator kill [agent_id]
│  └─ Mata agent específico (emergencia)
│
├─ /n8n list
│  └─ Workflows disponibles + próximo trigger
│
├─ /n8n run [workflow_id]
│  └─ Ejecuta manual (ej: /n8n run scan-tenants)
│
├─ /deploy
│  └─ Dispara GitHub Actions (auto push)
│
├─ /mission-control
│  └─ Link + QR a dashboard
│
└─ /logs [servicio]
   └─ Últimas 50 líneas de logs (hermes-api, postgres, etc)

Todas las acciones:
  ✅ Loguean en Mission Control (LogsViewer)
  ✅ Notifican al CEO
  ✅ Updatean AgentsMonitor en vivo
```

---

## 📅 N8N Workflows (NO Infinitos)

| Workflow | Trigger | Schedule | Duration | Notif |
|----------|---------|----------|----------|-------|
| **every-6h-scan** | Cron | 6am, 12pm, 6pm, 12am | ~2 min | ✅ Telegram |
| **on-new-tenant** | Webhook | on signup | ~5 min | ✅ Telegram |
| **daily-alerts** | Cron | 6am | ~3 min | ✅ Telegram |

**Garantía**: Cada workflow termina. No loops infinitos. Si error → retry once → notif CEO.

---

## ✅ Eficiencia de Recursos

### Memory Management

```
IDLE STATE:
├─ FastAPI: ~100MB
├─ PostgreSQL: ~200MB
├─ Redis: ~50MB
├─ Qdrant: ~150MB
├─ N8N: ~200MB
├─ Agents (0): 0MB
└─ TOTAL: ~700MB ✅ (very efficient)

RUNNING STATE (1 agent):
├─ Base services: ~700MB
├─ Agent (MYSTIC): ~300MB
└─ TOTAL: ~1000MB ✅ (within VPS limits)

RUNNING STATE (2 agents):
└─ TOTAL: ~1300MB ⚠️ (approaching limit)
   → Orchestrator mata agents no-críticos
   → Conserva solo CEO's task
```

### No Infinite Loops

✅ Agents: Spawn on demand, die on completion  
✅ N8N: Cron-triggered, no polling  
✅ Heartbeat: 30s interval (not continuous)  
✅ Logs: Streamed (not buffered)  
✅ Cache: TTL 1h (auto-expiry)  

---

## 🔗 Correlación: Todo sirve

```
ClawBot:
  └─ User input → Orchestrator → Agent → Result → Mission Control → CEO

Mission Control:
  ├─ Shows agent state (live)
  ├─ Shows logs (live)
  ├─ Shows tasks progress
  └─ CEO monitorea TODO

Orchestrator:
  ├─ Escucha ClawBot (Redis)
  ├─ Maneja agent lifecycle
  ├─ Reporta a Mission Control (WebSocket)
  └─ Garantiza eficiencia (RAM, TTL)

N8N:
  ├─ Automatiza tareas repetitivas
  ├─ Trigger-based (no polling)
  ├─ Notifica ClawBot cuando termina
  └─ Resultado visible en Mission Control

API:
  ├─ Responde /hermes/chat con RAG
  ├─ Responde /mystic/analyze con alertas
  ├─ Cachea en Redis
  └─ Datos reales para Mission Control
```

**Nada sobra. Todo colabora.**

---

## 🚀 Deployment

1. **DNS**: docs/DNS_SETUP.md
2. **DB Users**: infra/migrations/005_demo_users.sql
3. **GitHub Secrets**: 8 valores (scripts/setup-github-secrets.sh)
4. **git push main** → auto-deploy Vercel + VPS
5. **Explore**: https://sonoradigitalcorp.com/

---

**Estado**: ✅ Production Ready  
**Última actualización**: 2026-04-16  
**Arquitecto**: Claude Code + Gentleman.Programm  
**Filosofía**: Bot-first, eficiencia de recursos, zero infinites, total correlation
