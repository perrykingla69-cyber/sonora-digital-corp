# AGENT MAP — HERMES OS
> Abre Claude Code **desde el subdirectorio** del agente para cargar solo su contexto.
> Cross-domain: `mem_search "<keyword>"` en Engram.

## Agentes disponibles

| Agente | Directorio | `cd` para activar | Dominio |
|--------|-----------|-------------------|---------|
| **api** | `backend/` | `cd hermes-os/backend` | FastAPI, DB, auth, RLS, JWT |
| **bots** | `apps/clawbot/` | `cd hermes-os/apps/clawbot` | Telegram x4, WhatsApp, skills |
| **hermes** | `apps/hermes/` | `cd hermes-os/apps/hermes` | Orquestador IA, RAG, OpenRouter |
| **mystic** | `apps/mystic/` | `cd hermes-os/apps/mystic` | Shadow analyst, alertas CEO |
| **rag** | `agents/` | `cd hermes-os/agents` | AutoSeeder, Qdrant, embeddings |
| **frontend** | `frontend/` | `cd hermes-os/frontend` | Next.js, dashboard, landings |
| **infra** | `infra/` | `cd hermes-os/infra` | Docker, Nginx, VPS, N8N, CI/CD |

## Cómo trabajar con agentes

### Opción A — Claude Code por directorio (recomendado)
```bash
# Terminal en el subdirectorio → Claude Code solo carga ese CLAUDE.md
cd /home/mystic/hermes-os/backend
claude  # agent:api — contexto mínimo
```

### Opción B — Desde raíz con instrucción de dominio
```
Trabajemos en agent:api (backend/).
Ignora los demás directorios.
```

### Opción C — OpenCode en VPS
```bash
ssh vps "/home/mystic/.opencode/bin/opencode run -p 'tarea...' --agent hermes"
# OpenCode usa el CLAUDE.md del directorio donde corre
```

## Memoria cross-agente (Engram)
Cada agente escribe sus decisiones con `topic_key: agent/{nombre}`.
Para leer contexto de otro agente:
```
mem_search "agent/api"      → decisiones del backend
mem_search "agent/bots"     → decisiones de ClawBot
mem_search "agent/rag"      → estado del seeder
```

## Nota sobre duplicados
El repo tiene directorios legacy/paralelos. Los activos son:
- ✅ `apps/api/` — API activa en prod (root docker-compose.yml)
- ✅ `apps/clawbot/` — ClawBot activo (no `clawbot/`)
- ✅ `frontend/` — Frontend activo (no `apps/frontend/`)
- ✅ `apps/hermes/` + `apps/mystic/` — Agentes IA activos
- ⚠️ `backend/`, `apps/telegram-bot/`, `whatsapp/`, `clawbot/` — legacy/deprecated
