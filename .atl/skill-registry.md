# HERMES OS — Skill Registry

**Last updated**: 2026-04-20 | **Scope**: Project-level and user-level skills

## Project-Level Skills

### ClawBot Gateway
- **Path**: `agents/clawbot/SKILL.md`, `clawbot/SKILL.md`
- **Role**: Multi-channel gateway (Telegram CEO/Public/Alerts + WhatsApp via Evolution)
- **Triggers**: `/hermes`, `/mystic`, `/status`, `/tenants`, `/scan`, `/seed`, `/logs`, `/alerta`
- **Routing**: CEO (Luis Daniel) → full access; Public → tenant-scoped; Unknown → onboarding

## Project Conventions

### AGENTS.md (Project root)
- **Type**: Coding standards and style guide
- **Content**: Python FastAPI, TypeScript/React, Node.js/Telegram standards
- **Key rules**: Español in comments/messages, Type hints (Python), JWT field `usuario`, RLS `SET LOCAL`, logging (no print), docker compose v2

### CLAUDE.md (Project root)
- **Type**: Project guidance for Claude Code
- **Content**: Architecture overview, directories, gotchas, critical rules

## User-Level Skills

Skills in `~/.claude/skills/` are available globally. Project-specific skills override user-level ones.

---

## Stack Context (Auto-detected)

| Component | Details |
|-----------|---------|
| **Backend** | FastAPI (apps/api/), Python agents (fiscal, food, legal, code-review, etc.) |
| **Frontend** | Next.js 14 (dashboard, landing, mission-control), React + TypeScript |
| **Bots** | Telegraf (ClawBot: Node.js), telegram-bot (legacy), whatsapp-bridge |
| **Database** | PostgreSQL 16 (RLS multi-tenant), Redis, Qdrant (RAG) |
| **Infra** | Docker Compose v2, 11+ services, OpenRouter API |
| **Testing** | pytest (Python), Jest/Vitest expected (TS/Node) |

## Architecture Overview

```
Frontend (Next.js) + Dashboard
    ↓
ClawBot (Gateway: Telegram/WhatsApp via Evolution)
    ↓
HERMES (Orquestador IA: OpenRouter Gemini 2.0 Flash)
    ↓
PostgreSQL + Redis + Qdrant (RAG Híbrido)
    ↓
MYSTIC (Shadow Analyst) + N8N (Workflows)
```

**Agents**:
- **HERMES**: Orchestrator (never invents, always cites RAG sources)
- **MYSTIC**: Shadow analyst (strategic insights, hourly scans)
- **ClawBot**: Gateway (routes to correct brain)
- **AutoSeeder**: Background knowledge pipeline (seed by niche, embed, upsert)
- **Specialized**: Fiscal, Food, Legal, Code Review, Deployment, Monitoring agents

---

## Critical Rules

1. **Secrets**: Never in repo — use `infra/.env` (gitignored)
2. **RLS**: `SET LOCAL app.current_tenant_id` (transaction-scoped, safe with PgBouncer)
3. **JWT**: Field `usuario` (not `user`)
4. **Docker**: `docker compose v2` only
5. **Table `cierres_mes`**: Column `año` with literal ñ
6. **Logging**: No print() in production — use logging module (Python) or logger (Node)
7. **bcrypt**: Direct use, not passlib (incompatible)
8. **Container prefix**: `hermes_` (never `mystic_`)

---

## Directories

| Path | Role |
|------|------|
| `/backend/main.py` | Legacy monolith (147KB) |
| `/apps/api/` | FastAPI v2 bootstrap (modular) |
| `/apps/hermes/` | Orchestrator agent |
| `/apps/mystic/` | Strategic analyst agent |
| `/apps/clawbot/` | Multi-channel gateway |
| `/infra/` | docker-compose, nginx, SQL migrations |
| `/docs/` | Architecture, ADRs |
| `/agents/` | Specialized agents (RAG, seeders) |

---

## Tech Stack Summary

- **Backend runtime**: Python 3.11+ (FastAPI, SQLAlchemy, asyncpg)
- **Frontend framework**: Next.js 14 (App Router), React 18, TypeScript
- **Bot framework**: Telegraf.js, Evolution API (WhatsApp)
- **Database**: PostgreSQL 16 (RLS), Redis, Qdrant
- **Embedding**: nomic-embed-text via Ollama (768-dim, BM25 hybrid)
- **LLM**: OpenRouter (Gemini 2.0 Flash, GLM Z1 Rumination)
- **Container orchestration**: Docker Compose v2
- **IaC**: VPS Hostinger (IP in SSH config)

---

## Pending Artifacts

- [ ] `apps/api/CLAUDE.md` — API v2 bootstrap guide
- [ ] `packages/*/CLAUDE.md` — Shared library guides
- [ ] N8N workflow documentation — 18+ workflows require README

---

**Legend**: `🔴 Critical | 🟡 Important | 🟢 Backlog`
