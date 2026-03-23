# packages/workflow-runtime

Motor de ejecución de workflows N8N para MYSTIC.

## Instalación

```bash
pip install -e packages/workflow-runtime
```

## Uso

```python
from pathlib import Path
from workflow_runtime import WorkflowEngine, WorkflowLoader

# Configurar loader con directorio de workflows
loader = WorkflowLoader(Path("infra/n8n-workflows"))

# Configurar engine
engine = WorkflowEngine(
    n8n_base_url="http://localhost:5678",
    n8n_api_key="tu_api_key",
)
engine.set_loader(loader)

# Ejecutar workflow por ID
result = engine.execute("workflow-id-123", data={"key": "value"})
print(f"Status: {result.status}, Tiempo: {result.execution_time_ms}ms")

# Ejecutar workflow por nombre
result = engine.execute_by_name("Cierre Mensual", data={"mes": "enero"})

# Listar todos los workflows
workflows = loader.list_all()
for wf in workflows:
    print(f"- {wf.name} (trigger: {wf.trigger.type if wf.trigger else 'none'})")

# Ejecutar todos los workflows cron manualmente
results = engine.trigger_cron_workflows()
for r in results:
    print(f"{r.workflow_name}: {r.status}")
```

## Componentes

- `WorkflowLoader` - Carga definiciones desde archivos JSON de N8N
- `WorkflowEngine` - Ejecuta workflows vía API/webhook
- `WorkflowDefinition` - Modelo pydantic de un workflow
- `WorkflowExecutionResult` - Resultado estandarizado de ejecución

## Desarrollo

```bash
cd packages/workflow-runtime
pip install -e ".[dev]"
pytest
```
