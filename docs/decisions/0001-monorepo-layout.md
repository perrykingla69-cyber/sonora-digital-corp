# ADR 0001 — Monorepo Layout V2

## Estado
Accepted

## Decisión

Adoptamos una estructura monorepo basada en dominios:

- `apps/` para servicios y entradas principales,
- `packages/` para librerías compartidas,
- `workflows/` para automatizaciones versionadas,
- `infra/` para despliegue y operación,
- `docs/` para arquitectura, decisiones y producto,
- `tests/` para pruebas organizadas por capa.

## Motivación

Esta estructura separa aplicaciones de paquetes reutilizables, reduce acoplamiento y alinea el repositorio con la arquitectura objetivo de agentes, memoria, workflows y tooling interoperable.
