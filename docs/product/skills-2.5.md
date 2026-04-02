# Skills 2.5

Una Skill 2.5 es una capacidad reutilizable del sistema que combina:

- operación concreta,
- contrato estable,
- políticas de ejecución,
- telemetría,
- hooks de memoria,
- compatibilidad con API / CLI / workflows / MCP.

## Contrato mínimo

Toda skill debe declarar:

- `name`
- `version`
- `domain`
- `description`
- `input_schema`
- `output_schema`
- `timeout_seconds`
- `required_permissions`
- `tenant_aware`
- `api_exposed`
- `cli_exposed`
- `workflow_exposed`
- `mcp_exposed`

## Reglas de diseño

1. Una skill hace una sola cosa bien.
2. Los agentes coordinan; las skills ejecutan.
3. Toda skill debe ser observable.
4. Toda skill sensible debe declarar efectos laterales.
5. Toda skill expuesta debe estar versionada.
