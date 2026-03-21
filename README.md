# MYSTIC AI Operating System

Plataforma operativa de IA para **Sonora Digital Corp**: backend multi-tenant, automatización con n8n, memoria/RAG, canales conversacionales y una ruta clara hacia runtime de agentes, CLI y MCP.

## Estado actual del repo

El repositorio hoy contiene una base funcional de producción con:

- API principal en **FastAPI**.
- Frontend en **Next.js 14**.
- Servicio **WhatsApp**.
- **Bot** operativo.
- Infraestructura con **PostgreSQL, Redis, Ollama, n8n y Qdrant**.
- Documentación arquitectónica y workflows n8n.

## Dirección v2 ya aterrizada

Como primer paso real hacia la arquitectura v2, el repo ya incluye la nueva estructura base para migración incremental:

```text
sonora-digital-corp/
├── apps/              # entradas ejecutables v2
├── packages/          # librerías compartidas v2
├── workflows/         # workflows catalogados y versionados
├── infra/             # despliegue y operación
├── docs/              # arquitectura, ADRs, runbooks y producto
├── backend/           # implementación legacy actual
├── frontend/          # implementación legacy actual
├── bot/               # implementación legacy actual
├── whatsapp/          # implementación legacy actual
└── tests/             # pruebas existentes
```

La migración será incremental: la aplicación legacy sigue viva mientras se mueven responsabilidades a `apps/` y `packages/`.

## Entradas principales

### Legacy

```bash
python backend/main.py
```

### V2 bootstrap compatible

```bash
uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000
```

## Quick start

```bash
# Backend legacy
python backend/main.py

# Backend v2 wrapper
uvicorn apps.api.app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend legacy
cd frontend && npm install && npm run dev

# Tests backend
python -m pytest tests/ -v
```

## Roadmap de implementación

### Fase 1 — Estructura monorepo
- `apps/`, `packages/`, `workflows/`, `docs/architecture`, `docs/decisions`.
- Bootstrap modular de API v2 en `apps/api/app/main.py` con routers reales de sistema, auth, tenants y facturas.

### Fase 2 — Backend modular
- dividir `backend/main.py` en routers, servicios, integraciones, settings, schemas y router agregador.

### Fase 3 — Memory OS
- Postgres + Redis + Qdrant + evidence layer.
- Primer corte v2: ingestión, consulta, borrado, métricas y feedback básico sobre memoria persistida en `.data` (configurable con `MEMORY_DATA_DIR`) con filtros por tenant/tipo, snippets de evidencia, métricas simples de búsqueda/feedback y preparada para adaptadores futuros.

### Fase 4 — Agent Runtime + Skills 2.5
- registry, runtime, sessions y policies.

### Fase 5 — MCP + CLI
- tool exposure gobernada y operable desde Claude Code/CLI.

### Fase 6 — Workflows + Approvals + Autonomy
- n8n catalogado, approvals y autonomía controlada.

### Fase 7 — Command Center
- consola operativa para tareas, workflows, approvals, memoria y observabilidad.

### Fase 8 — Evals + Security + CI/CD
- hardening de producción, gobierno, evaluaciones y despliegue seguro.

## Documentos clave nuevos

- `docs/architecture/target-architecture-v2.md`
- `docs/product/skills-2.5.md`
- `docs/decisions/0001-monorepo-layout.md`
- `docs/decisions/0002-skills-contract.md`

## Filosofía

- **Open-source first**.
- **Migración incremental sin romper producción**.
- **Memoria y evidencia antes de autonomía agresiva**.
- **Policies y observabilidad antes de exposición externa**.
- **Una sola base de código, múltiples superficies de operación**.
