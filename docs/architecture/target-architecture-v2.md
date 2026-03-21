# Target Architecture V2 — Sonora Digital / MYSTIC

## Propósito

Esta arquitectura define la evolución de la plataforma Sonora Digital / MYSTIC hacia un sistema operativo de IA orientado a:

- automatización empresarial,
- memoria persistente,
- RAG operativo,
- herramientas interoperables vía MCP,
- ejecución multi-canal,
- despliegue soberano/open source,
- y operación segura en producción.

## Principios de diseño

1. **MCP-first**.
2. **RAG-native**.
3. **Automation-driven**.
4. **Privacy-aware**.
5. **CLI-operable**.
6. **Multi-tenant by design**.
7. **Observability by default**.

## Capas del sistema

1. **Experience Layer**: dashboard web, WhatsApp, Telegram bot y CLI.
2. **API / Application Layer**: FastAPI, auth, tenants, RBAC y APIs públicas/internas.
3. **Orchestration / Agent Layer**: task router, runtime, skill registry, sessions y policies.
4. **Memory Layer**: PostgreSQL + Redis + Qdrant.
5. **Automation Layer**: n8n, webhooks, approvals y jobs.
6. **Inference Layer**: reglas, modelos locales, open-source y premium.
7. **Operations Layer**: observabilidad, backups, CI/CD y evaluaciones.

## Roadmap de adopción

### Fase 1
- reorganizar repo,
- modularizar backend,
- separar infraestructura.

### Fase 2
- formalizar memory layer,
- retrieval base,
- Qdrant como store principal semántico.

### Fase 3
- runtime de agentes,
- skill registry,
- policies.

### Fase 4
- MCP server,
- CLI,
- workflows versionados.

### Fase 5
- evals,
- seguridad avanzada,
- observabilidad semántica.
