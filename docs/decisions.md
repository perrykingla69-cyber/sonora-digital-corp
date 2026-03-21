# Decisiones de Arquitectura — Sonora Digital Corp

## ADR-001: Brain IA integrado en mystic_api (no contenedor separado)
**Fecha:** 20 Marzo 2026
**Estado:** Activo

**Contexto:**
VPS Hostinger 4GB RAM. Con 9 contenedores corriendo, la RAM llega al 84%.
Un contenedor mystic_brain separado en :8001 agregaría ~300MB overhead.

**Decisión:**
Brain IA (RAG + Ollama + Qdrant) opera dentro de mystic_api en :8000.
Rutas: /api/brain/ask | /api/brain/swarm | /api/brain/feedback

**Consecuencias:**
- Ahorro ~300MB RAM
- Un punto de deploy (no dos imágenes)
- Si la API cae, el Brain también cae (aceptable en fase actual)

**Revisar cuando:**
- RAM del VPS supere el 90% de uso sostenido
- Se agregue un segundo tenant activo con uso intensivo de Brain
