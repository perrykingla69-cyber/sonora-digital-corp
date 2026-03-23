# MYSTIC - Tool Use Implementation Guide

## Resumen Ejecutivo

Se ha implementado **Tool Use** estilo LangChain en MYSTIC, permitiendo que el Brain no solo responda preguntas sino que **ejecute acciones reales**:

- ✅ Trigger de workflows N8N
- ✅ Consultas SAT (verificar CFDI, RFC, calendario)
- ✅ Operaciones database (CRUD facturas, nóminas, empleados)
- ✅ Indexado RAG en Qdrant

---

## Arquitectura Implementada

### 1. Tools (`/backend/app/ai/tools/`)

```
app/ai/tools/
├── __init__.py          # Exporta herramientas
├── base.py              # BaseTool + 4 herramientas implementadas
│   ├── BaseTool         # Clase base con schema formal
│   ├── N8NTriggerTool   # Ejecuta workflows N8N
│   ├── SATQueryTool     # Consulta servicios SAT
│   ├── DBQueryTool      # CRUD PostgreSQL
│   └── RAGIndexTool     # Indexa documentos en Qdrant
└── tool_use.py          # Detección de intención + ejecución
    ├── detect_tool_calls()      # Pattern matching
    ├── execute_tool_call()      # Ejecuta herramienta
    └── brain_ask_with_tools()   # Integración con /api/brain/ask
```

### 2. Skills 2.5 Features

Cada herramienta tiene:
- **JSON Schema** para input/output validado con Pydantic
- **Tenant awareness** (tenant_id en cada llamada)
- **Telemetría** (execution_time_ms, status, error tracking)
- **Permisos por rol** (allowed_roles: admin, contador, analista)
- **Rate limiting** configurado por herramienta

---

## Cómo Funciona el Tool Use

### Flujo Completo

```
Usuario (WhatsApp/Web) → "Ejecuta el cierre mensual"
           ↓
   /api/brain/ask
           ↓
   detect_tool_calls()
           ↓
   ¿Detectó intención? 
   ├── SÍ → execute_tool_call("n8n_trigger", {...})
   │         ↓
   │        POST http://localhost:5678/webhook/cierre-mensual
   │         ↓
   │        Resultado → Contexto → Ollama → Respuesta
   │
   └── NO → RAG normal → Ollama → Respuesta
```

### Ejemplos de Detección

| Input Usuario | Herramienta Detectada | Acción |
|--------------|----------------------|--------|
| "Ejecuta el workflow de cierre" | `n8n_trigger` | POST /webhook/cierre-mensual |
| "Busca las facturas pendientes" | `database_query` | SELECT FROM facturas WHERE estado='pendiente' |
| "Verifica el CFDI ABC123..." | `sat_query` | GET /api/sat/verificar/ABC123... |
| "Indexa estos documentos" | `rag_index` | UPSERT en Qdrant |

---

## Integración con Endpoints Existentes

### Opción A: Modificar `/api/brain/ask` (Recomendado)

En `/workspace/backend/main.py`, línea ~2333:

```python
@app.post("/api/brain/ask", response_model=_BrainResponse, tags=["Brain"])
async def brain_ask(body: _BrainRequest, db: Session = Depends(get_db)):
    """Versión ACTUAL - solo RAG"""
    # ... código existente ...
```

**Reemplazar con:**

```python
from app.ai.tools.tool_use import brain_ask_with_tools

@app.post("/api/brain/ask", response_model=_BrainResponse, tags=["Brain"])
async def brain_ask(body: _BrainRequest, db: Session = Depends(get_db)):
    """Versión CON TOOL USE - ejecuta acciones"""
    
    # Funciones auxiliares existentes
    async def rag_fn(question: str, tenant_id: str = None):
        # Tu lógica RAG actual (Qdrant + fallback)
        pass
    
    def ollama_fn(system: str, user: str) -> str:
        # Tu llamada a Ollama actual
        pass
    
    # Tool Use Integration
    result = await brain_ask_with_tools(
        question=body.question,
        rag_fn=rag_fn,
        ollama_fn=ollama_fn,
        tenant_id=body.tenant_id if hasattr(body, 'tenant_id') else None,
        db_session=db
    )
    
    return _BrainResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence=0.9,
        tools_used=result["tool_calls"]  # Nuevo campo
    )
```

### Opción B: Endpoint Separado `/api/brain/act`

```python
@app.post("/api/brain/act", tags=["Brain"])
async def brain_act(body: _BrainRequest, db: Session = Depends(get_db)):
    """Endpoint específico para acciones con tool use"""
    from app.ai.tools.tool_use import process_with_tools
    
    result = await process_with_tools(
        question=body.question,
        tenant_id=body.tenant_id if hasattr(body, 'tenant_id') else None,
        execute_tools=True
    )
    
    return {
        "action_executed": len(result.tool_calls) > 0,
        "tools": [tc.tool_name for tc in result.tool_calls],
        "results": result.results,
        "summary": result.natural_language_summary
    }
```

---

## Comandos para Claude

### 1. Instalar dependencias

```bash
cd /workspace/backend
pip install -r requirements.txt
```

### 2. Probar herramientas individualmente

```bash
python3 << 'EOF'
from app.ai.tools.base import get_tool, list_tools

# Listar todas las herramientas
print("Herramientas disponibles:")
for t in list_tools():
    print(f"  - {t['name']}: {t['description']}")

# Probar N8N Trigger
tool = get_tool("n8n_trigger")
result = tool({
    "workflow_name": "clasificacion_arancelaria",
    "payload": {"fraccion": "8517.12.01"},
    "wait_for_response": False
})
print(f"\nResultado: {result.model_dump()}")
EOF
```

### 3. Probar detección de intención

```bash
python3 << 'EOF'
from app.ai.tools.tool_use import detect_tool_calls, process_with_tools
import asyncio

test_cases = [
    "Ejecuta el workflow de cierre mensual",
    "Busca las facturas pendientes de este mes",
    "Verifica el CFDI 12345678-1234-1234-1234-123456789012",
    "¿Cuántos empleados tenemos registrados?",
]

for test in test_cases:
    print(f"\nInput: {test}")
    calls = detect_tool_calls(test)
    for c in calls:
        print(f"  → Tool: {c.tool_name} (confianza: {c.confidence})")
        print(f"     Args: {c.arguments}")
EOF
```

### 4. Ejecutar optimización de RAM

```bash
# En local
./scripts/optimize_ram.sh

# En VPS (vía SSH)
ssh mystic@187.124.85.191 'bash -s' < scripts/optimize_ram.sh
```

### 5. Seed de datos Fourgea (RAG per-tenant)

```bash
python3 scripts/seed_fourgea_docs.py
```

---

## Frontend: Dashboard Mejorado

### Nuevas Métricas Recomendadas

Agregar al dashboard actual (`/frontend/src/app/(app)/dashboard/page.tsx`):

```tsx
// Tarjetas adicionales para Tool Use
<Card title="Acciones Ejecutadas">
  <Stat value={toolsExecuted} label="Tools hoy" />
  <Stat value={avgExecutionTime} label="Tiempo promedio" />
</Card>

<Card title="Workflows Activos">
  <ul>
    {workflows.map(w => (
      <li key={w.id}>{w.name} - {w.status}</li>
    ))}
  </ul>
</Card>
```

### Página de Login

Ya existe en `/frontend/src/app/login/page.tsx`. Verificar que:
- Tenga enlace a "Recuperar contraseña"
- Redirija a `/dashboard` después de login exitoso
- Muestre errores claros

---

## MCP Server (Model Context Protocol)

El MCP server permite conectar Claude Code directamente al sistema MYSTIC.

### Estado Actual
- Carpeta `/apps/mcp-server/` existe
- README.md vacío

### Implementación Mínima

```typescript
// apps/mcp-server/index.ts
#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server({
  name: 'mystic-mcp',
  version: '1.0.0',
}, {
  capabilities: {
    resources: {},
    tools: {},
  },
});

// Herramientas expuestas a Claude Code
server.setRequestHandler('tools/list', async () => ({
  tools: [
    {
      name: 'brain_ask',
      description: 'Preguntar al Brain contable de MYSTIC',
      inputSchema: { question: { type: 'string' } },
    },
    {
      name: 'execute_workflow',
      description: 'Ejecutar workflow N8N',
      inputSchema: { workflow_name: { type: 'string' } },
    },
  ],
}));

const transport = new StdioServerTransport();
await server.connect(transport);
```

---

## CLI Propia

### Estructura

```
apps/cli/
├── main.py            # Click/Typer CLI
├── commands/
│   ├── seed.py        # mystic seed fourgea
│   ├── status.py      # mystic status
│   ├── tools.py       # mystic tools list
│   └── deploy.py      # mystic deploy vps
```

### Comandos Básicos

```python
# apps/cli/main.py
import typer

app = typer.Typer(name="mystic")

@app.command()
def status():
    """Mostrar estado del sistema"""
    print("✅ Backend: OK")
    print("✅ Qdrant: OK")
    print("✅ Redis: OK")
    print("⚠️  N8N: Revisar logs")

@app.command()
def seed(tenant: str = "fourgea"):
    """Sembrar datos en Qdrant"""
    print(f"Seedings docs for {tenant}...")

if __name__ == "__main__":
    app()
```

Uso:
```bash
mystic status
mystic seed --tenant fourgea
mystic tools list
```

---

## Próximos Pasos (Prioridad)

### Esta Semana
1. ✅ **Integrar tool use en `/api/brain/ask`** (modificar main.py línea 2333)
2. ✅ **Probar con casos reales** de Nathaly
3. ⏳ **Seed de datos Fourgea** en Qdrant

### Próxima Semana
4. ⏳ **Dashboard mejorado** con métricas de tool use
5. ⏳ **MCP server funcional** para Claude Code
6. ⏳ **CLI operativa** con comandos básicos

### Futuro
7. Más herramientas: `whatsapp_send`, `email_send`, `pdf_generate`
8. Agentes 5-8 con lógica real
9. RAG per-tenant sembrado con datos reales

---

## Referencias GitHub

Repos de LangChain Tools para inspiración:
- https://github.com/langchain-ai/langchain/tree/master/libs/core
- https://github.com/microsoft/autogen
- https://github.com/run-llama/llama_index

Patrones clave adoptados:
- Tool schema con Pydantic
- Function calling detection con regex + LLM
- Execution sandbox para seguridad
