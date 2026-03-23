# packages/shared-types

Paquete interno de tipos compartidos para MYSTIC.

## Instalación

```bash
pip install -e packages/shared-types
```

## Uso

```python
from mystic_types import TenantConfig, BrainRequest, BrainResponse, ToolDefinition

# Crear configuración de tenant
tenant = TenantConfig(
    id="fourgea-001",
    name="Fourgea S.A.",
    rfc="FOU850101ABC",
    plan="pro"
)

# Request al Brain
request = BrainRequest(
    query="¿Qué es el RESICO?",
    tenant_id="fourgea-001"
)
```

## Tipos disponibles

- `TenantConfig` - Configuración de cliente/empresa
- `UserContext` - Contexto de usuario en sesión
- `BrainRequest` / `BrainResponse` - Requests y respuestas del Brain IA
- `ToolDefinition` / `ToolResult` - Herramientas ejecutables
- `SkillDefinition` - Skills con contexto
- `WorkflowTrigger` - Triggers de workflows N8N
- `RAGDocument` / `EmbeddingConfig` - Documentos y config de RAG

## Desarrollo

```bash
cd packages/shared-types
pip install -e ".[dev]"
pytest
```
