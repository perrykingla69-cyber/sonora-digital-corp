# Plan de sprints siguientes — v2

## Sprint 3 — Cerrar Fase 2
- mover más endpoints legacy a `apps/api/app/api/*`
- homologar dependencias, response models y manejo de errores
- reducir el acoplamiento directo con `backend/main.py`
- agregar pruebas de integración por módulo (`auth`, `facturas`, `empleados`, `contactos`)

## Sprint 4 — Profundizar Memory OS
- reemplazar JSON local por adaptadores compatibles con Postgres/Qdrant/Redis
- agregar evidencia/trace de recuperación y metadatos de origen ✅
- incorporar filtros por tenant y por tipo de documento ✅
- medir feedback y calidad de recuperación con métricas simples ✅

## Sprint 5 — Runtime + Skills
- crear registry de skills ✅ (cargado desde catálogo/config)
- introducir sesiones/runtime de agentes ✅
- definir policies básicas por tenant y por canal ✅
- exponer endpoints v2 básicos para skills/sesiones/autorización ✅

## Sprint 6 — MCP + CLI + Workflows
- exponer herramientas vía MCP
- unificar CLI operativa
- catalogar y versionar workflows n8n
