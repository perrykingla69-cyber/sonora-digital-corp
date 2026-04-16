# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# HERMES AI OS — Guía Compacta

**Proyecto**: AI Orchestrator SaaS para PYMEs mexicanas (contabilidad, CRM, Brain IA).  
**Dueño**: Luis Daniel Guerrero Enciso  
**Repo**: `github.com/perrykingla69-cyber/sonora-digital-corp`  
**Idioma**: Español siempre

---

## 🏗️ ARQUITECTURA (BIG PICTURE)

Monorepo en transición legacy→v2 con 3 agentes distribuidos:

```
Frontend (Next.js) + Dashboard
    ↓
ClawBot (Gateway: Telegram/WhatsApp)
    ↓
HERMES (Orquestador IA) ← OpenRouter API
    ↓
PostgreSQL + Redis + Qdrant (RAG)
    ↓
MYSTIC (Shadow analyst) + N8N (Workflows)
```

**Servicios**: 11 containers (postgres, redis, qdrant, evolution, n8n, hermes-api, hermes-agent, mystic-agent, clawbot, content-agent, frontend).

---

## 🔐 REGLAS CRÍTICAS

- **Secretos**: NUNCA en repo. Solo `infra/.env.example` en git; `infra/.env` es gitignored.
- **JWT**: Field `usuario` (no `user`), revocación por JTI en Redis.
- **RLS**: Usar `SET LOCAL app.current_tenant_id TO 'uuid'` (transaction-scoped, no global).
- **Docker**: `docker compose v2` (nunca `docker-compose` v1).
- **Git VPS**: `git -C /home/mystic/sonora-digital-corp <cmd>`.

---

## ⚡ COMANDOS ESENCIALES

```bash
# Local
make up                    # Levanta stack
make down                  # Apaga
make logs                  # Ver logs (all)
make ps                    # Estado containers

# VPS
make vps-deploy            # git pull + deploy.sh
make vps-logs              # Logs en VPS

# Backend
python -m pytest tests/ -v # Tests
uvicorn apps.api.app.main:app --reload  # API v2

# Frontend
cd frontend && npm run dev # Dev server (3000)
```

---

## 📂 DIRECTORIOS CLAVE

| Path | Rol |
|------|-----|
| `/backend/main.py` | LEGACY monolítico (147KB) |
| `/apps/api/` | FastAPI v2 bootstrap (modular) |
| `/apps/hermes/` | Agente orquestador |
| `/apps/mystic/` | Agente estratega |
| `/apps/clawbot/` | Bot ejecutor |
| `/infra/` | docker-compose, nginx, SQL |
| `/docs/` | Architecture, ADRs |

---

## 🔄 GOTCHAS TÉCNICOS

- **RLS**: `SET LOCAL` (seguro) vs `SET` global (falla con PgBouncer).
- **bcrypt**: Directo, no passlib (incompatible).
- **Ollama**: Pausar si no se usa (RAM limitada en VPS).
- **Tabla `cierres_mes`**: Columna `año` con ñ literal.
- **Frontend**: Rebuild completo al cambiar código (variables en `build.args`).

---

## 📋 PENDIENTES CRÍTICOS

- 🔴 `MP_ACCESS_TOKEN` (MercadoPago) — faltante
- 🔴 `WHATSAPP_NUMBER` (Chip Telcel) — faltante
- 🟡 Modularizar backend legacy → routers v2

---

## 📚 REFERENCIAS EXTENDIDAS

Para detalles completos, ver:
- `docs/CLAUDE-extended.md` — Stack técnico, variables env, configuración
- `docs/architecture/` — ADRs, diseño del sistema
- `AGENTS.md` — Coding standards (Python, TypeScript, Node.js)

---

## 🎯 PALABRA CLAVE ESPECIAL

`.DENIURGO` (de Luis Daniel) → auto-check:
```
mem_context + health checks (docker, API, git status)
Reportar: ✅ OK / ⚠️ Atención / 🔴 Caído
Top 3 acciones
```

---

**Última actualización**: 2026-04-14 | **Versión**: 2.2 (compacta)
