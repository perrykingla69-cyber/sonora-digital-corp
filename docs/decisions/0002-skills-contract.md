# ADR 0002 — Skills 2.5 Contract

## Estado
Accepted

## Decisión

Adoptamos Skills 2.5 como contrato estándar para capacidades del sistema.

Toda skill debe incluir:

- identidad,
- input/output schema,
- política de permisos,
- timeout,
- telemetría,
- hooks de memoria,
- exposición controlada por API / CLI / workflows / MCP.

## Resultado esperado

El sistema crecerá por composición de capacidades gobernadas y no por acumulación de lógica dispersa.
