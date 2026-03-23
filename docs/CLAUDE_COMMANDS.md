# MYSTIC - Comandos Maestros para Claude

## 🚀 Implementación Rápida (Copiar y Pegar)

### 1. Instalar dependencias nuevas

```bash
cd /workspace/backend
pip install pydantic>=2.5.0
```

### 2. Verificar que las herramientas existen

```bash
ls -la /workspace/backend/app/ai/tools/
# Debe mostrar: base.py, tool_use.py
```

### 3. Probar herramientas

```bash
cd /workspace/backend
python3 << 'EOF'
import sys
sys.path.insert(0, '/workspace/backend')

from app.ai.tools.base import list_tools, get_tool

print("=== HERRAMIENTAS DISPONIBLES ===\n")
for t in list_tools():
    print(f"🔧 {t['name']}")
    print(f"   {t['description']}")
    print(f"   Categoría: {t['category']}")
    print(f"   Roles: {', '.join(t['allowed_roles'])}")
    print()

# Probar ejecución
print("\n=== PRUEBA DE EJECUCIÓN ===\n")
tool = get_tool("database_query")
if tool:
    print(f"✅ Herramienta cargada: {tool.name}")
else:
    print("❌ Error cargando herramienta")
EOF
```

### 4. Probar detección de intención

```bash
cd /workspace/backend
python3 << 'EOF'
import sys
sys.path.insert(0, '/workspace/backend')

from app.ai.tools.tool_use import detect_tool_calls

test_cases = [
    ("Ejecuta el workflow de cierre mensual", "n8n_trigger"),
    ("Busca las facturas pendientes", "database_query"),
    ("Verifica el CFDI 12345678-ABCD-EFGH-1234-123456789012", "sat_query"),
    ("¿Cuántos empleados tenemos?", "database_query"),
    ("Esto es solo una pregunta", None),
]

print("=== PRUEBA DE DETECCIÓN DE INTENCIÓN ===\n")
for input_text, expected in test_cases:
    calls = detect_tool_calls(input_text)
    detected = calls[0].tool_name if calls else None
    status = "✅" if detected == expected else "❌"
    print(f"{status} Input: {input_text[:50]}...")
    if detected:
        print(f"   Detectado: {detected} (confianza: {calls[0].confidence})")
    else:
        print(f"   Sin herramienta detectada (esperado: {expected})")
    print()
EOF
```

### 5. Integrar Tool Use en main.py

**IMPORTANTE:** Esto modifica `/workspace/backend/main.py`

```bash
cd /workspace/backend

# Backup primero
cp main.py main.py.backup.$(date +%Y%m%d_%H%M%S)

# Agregar import al inicio del archivo (después de los otros imports)
sed -i '/^from security import/a from app.ai.tools.tool_use import brain_ask_with_tools' main.py

echo "✅ Import agregado. Ahora modificar la función brain_ask manualmente."
```

### 6. Modificar endpoint /api/brain/ask

Buscar en main.py la línea ~2333 donde está `@app.post("/api/brain/ask"` y reemplazar la función completa con:

```python
@app.post("/api/brain/ask", response_model=_BrainResponse, tags=["Brain"])
async def brain_ask(body: _BrainRequest, db: Session = Depends(get_db)):
    """
    Brain con Tool Use - responde preguntas Y ejecuta acciones
    """
    start_time = datetime.now()
    
    # --- Cache Check ---
    cache_key = _make_cache_key(body.context, body.question)
    cached = _redis.get(cache_key) if _redis else None
    if cached:
        try:
            return _BrainResponse(**json.loads(cached))
        except Exception:
            pass
    
    # --- Funciones auxiliares para tool use ---
    async def rag_fn(question: str, tenant_id: str = None):
        """Obtiene contexto RAG desde Qdrant"""
        from app.ai.swarm.queen import _search_qdrant
        try:
            chunks = await _search_qdrant(question, collection="general", limit=3)
            return chunks
        except Exception as e:
            logging.warning(f"RAG failed: {e}")
            return []
    
    def ollama_fn(system: str, user: str) -> str:
        """Llama a Ollama DeepSeek R1"""
        import httpx
        try:
            resp = httpx.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "deepseek-r1:latest",
                    "prompt": user,
                    "system": system,
                    "stream": False,
                },
                timeout=60.0
            )
            return resp.json().get("response", "")
        except Exception as e:
            logging.error(f"Ollama failed: {e}")
            raise
    
    # --- Tool Use Integration ---
    try:
        result = await brain_ask_with_tools(
            question=body.question,
            rag_fn=rag_fn,
            ollama_fn=ollama_fn,
            tenant_id=getattr(body, 'tenant_id', None),
            db_session=db
        )
        
        answer = result["answer"]
        sources = result.get("sources", [])
        tools_used = result.get("tool_calls", [])
        
    except Exception as e:
        logging.error(f"Brain ask failed: {e}")
        answer = f"Error procesando tu pregunta: {str(e)}"
        sources = []
        tools_used = []
    
    # --- Persistir sesión ---
    session = BrainSession(
        context=body.context,
        question=body.question,
        answer=answer,
        sources=json.dumps(sources),
        metadata_json=json.dumps({"tools_used": tools_used}) if tools_used else "{}"
    )
    db.add(session)
    db.commit()
    
    # --- Cache respuesta ---
    if _redis:
        try:
            payload = {
                "answer": answer,
                "context": body.context,
                "question": body.question,
                "sources": sources,
                "confidence": 0.9,
            }
            _redis.setex(cache_key, 3600, json.dumps(payload))
        except Exception:
            pass
    
    # --- Métricas ---
    elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)
    
    return _BrainResponse(
        answer=answer,
        context=body.context,
        question=body.question,
        sources=sources,
        confidence=0.9,
        elapsed_ms=elapsed_ms,
        tools_used=tools_used  # Nuevo campo
    )
```

### 7. Ejecutar optimización de RAM

```bash
chmod +x /workspace/scripts/optimize_ram.sh
/workspace/scripts/optimize_ram.sh
```

### 8. Seed de datos Fourgea en Qdrant

```bash
cd /workspace
python3 scripts/seed_fourgea_docs.py
```

### 9. Reiniciar servicios

```bash
# Local
docker-compose restart backend

# VPS
ssh mystic@187.124.85.191 'cd ~/sonora-digital-corp && docker-compose -f infra/docker-compose.vps.yml restart backend'
```

### 10. Verificar logs

```bash
# Local
docker logs -f mystic-backend-1

# VPS
ssh mystic@187.124.85.191 'docker logs -f mystic-backend-1'
```

---

## 📊 Frontend: Mejoras Recomendadas

### Dashboard - Agregar métricas de Tool Use

Editar `/workspace/frontend/src/app/(app)/dashboard/page.tsx`:

```tsx
// Agregar después de las tarjetas existentes
<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
  <Card title="🛠️ Acciones Ejecutadas">
    <div className="text-2xl font-bold text-sovereign-gold">{toolsToday || 0}</div>
    <p className="text-xs text-sovereign-muted">Tools ejecutadas hoy</p>
  </Card>
  
  <Card title="⏱️ Tiempo Promedio">
    <div className="text-2xl font-bold text-sovereign-gold">{avgTime || '—'}ms</div>
    <p className="text-xs text-sovereign-muted">Respuesta Brain</p>
  </Card>
  
  <Card title="🔄 Workflows Activos">
    <div className="text-2xl font-bold text-sovereign-gold">{activeWorkflows || 12}</div>
    <p className="text-xs text-sovereign-muted">N8N workflows</p>
  </Card>
</div>
```

### Login Page - Verificar

La página ya existe en `/workspace/frontend/src/app/login/page.tsx`. Solo verificar:

```bash
cat /workspace/frontend/src/app/login/page.tsx | grep -A 5 "handleSubmit"
# Debe tener redirección a /dashboard después de login exitoso
```

---

## 🔧 MCP Server - Implementación Mínima

### 1. Crear archivo principal

```bash
mkdir -p /workspace/apps/mcp-server
cat > /workspace/apps/mcp-server/index.ts << 'EOF'
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

server.setRequestHandler('tools/list', async () => ({
  tools: [
    {
      name: 'brain_ask',
      description: 'Preguntar al Brain contable de MYSTIC',
      inputSchema: {
        type: 'object',
        properties: {
          question: { type: 'string', description: 'Pregunta fiscal/contable' },
        },
        required: ['question'],
      },
    },
    {
      name: 'execute_workflow',
      description: 'Ejecutar workflow N8N',
      inputSchema: {
        type: 'object',
        properties: {
          workflow_name: { type: 'string' },
          payload: { type: 'object' },
        },
        required: ['workflow_name'],
      },
    },
  ],
}));

server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === 'brain_ask') {
    const response = await fetch('http://localhost:8000/api/brain/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: args.question }),
    });
    return { content: await response.json() };
  }
  
  if (name === 'execute_workflow') {
    const response = await fetch(`http://localhost:5678/webhook/${args.workflow_name}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(args.payload || {}),
    });
    return { content: await response.json() };
  }
  
  throw new Error(`Tool ${name} not found`);
});

const transport = new StdioServerTransport();
await server.connect(transport);
EOF
```

### 2. Instalar dependencias

```bash
cd /workspace/apps/mcp-server
npm init -y
npm install @modelcontextprotocol/sdk
```

---

## 🖥️ CLI - Implementación Mínima

### 1. Crear estructura

```bash
mkdir -p /workspace/apps/cli/commands
cat > /workspace/apps/cli/main.py << 'EOF'
#!/usr/bin/env python3
"""MYSTIC CLI - Command line interface"""

import typer
import sys
import os

app = typer.Typer(name="mystic", help="MYSTIC Contable CLI")

@app.command()
def status():
    """Mostrar estado del sistema"""
    print("🔍 Verificando servicios MYSTIC...\n")
    
    checks = [
        ("Backend API", "curl -s http://localhost:8000/docs"),
        ("Qdrant", "curl -s http://localhost:6333"),
        ("Redis", "redis-cli ping"),
        ("PostgreSQL", "pg_isready -h localhost"),
    ]
    
    for name, cmd in checks:
        try:
            result = os.system(f"{cmd} > /dev/null 2>&1")
            status = "✅ OK" if result == 0 else "❌ DOWN"
        except:
            status = "❌ ERROR"
        print(f"  {name}: {status}")

@app.command()
def seed(tenant: str = typer.Option("fourgea", help="Tenant ID")):
    """Sembrar datos en Qdrant"""
    print(f"🌱 Sembrando datos para tenant: {tenant}")
    os.system(f"python3 /workspace/scripts/seed_{tenant}_docs.py")

@app.command()
def tools():
    """Listar herramientas disponibles"""
    sys.path.insert(0, '/workspace/backend')
    from app.ai.tools.base import list_tools
    
    print("🛠️  Herramientas MYSTIC:\n")
    for t in list_tools():
        print(f"  • {t['name']}: {t['description']}")

@app.command()
def optimize():
    """Optimizar uso de RAM"""
    print("🔧 Optimizando memoria...")
    os.system("/workspace/scripts/optimize_ram.sh")

if __name__ == "__main__":
    app()
EOF

chmod +x /workspace/apps/cli/main.py
```

### 2. Instalar Typer

```bash
pip install typer
```

### 3. Usar CLI

```bash
cd /workspace/apps/cli
python3 main.py status
python3 main.py tools
python3 main.py seed --tenant fourgea
```

---

## ✅ Checklist Final

```bash
# Verificar todo instalado
echo "=== CHECKLIST ==="
echo -n "✅ Tools module: "
[ -f /workspace/backend/app/ai/tools/base.py ] && echo "OK" || echo "MISSING"

echo -n "✅ Tool Use module: "
[ -f /workspace/backend/app/ai/tools/tool_use.py ] && echo "OK" || echo "MISSING"

echo -n "✅ Optimize script: "
[ -f /workspace/scripts/optimize_ram.sh ] && echo "OK" || echo "MISSING"

echo -n "✅ Documentation: "
[ -f /workspace/docs/TOOL_USE_IMPLEMENTATION.md ] && echo "OK" || echo "MISSING"

echo -n "✅ Pydantic installed: "
python3 -c "import pydantic" 2>/dev/null && echo "OK" || echo "MISSING"
```

---

## 🆘 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'app.ai.tools'"

```bash
# Asegurar que el path esté configurado
export PYTHONPATH=/workspace/backend:$PYTHONPATH

# O agregar al inicio de main.py
echo "import sys; sys.path.insert(0, '/workspace/backend')" >> /workspace/backend/main.py
```

### Error: "Pydantic validation error"

```bash
# Verificar versión
pip show pydantic

# Actualizar si es necesario
pip install --upgrade pydantic>=2.5.0
```

### Error: "Qdrant connection refused"

```bash
# Verificar Qdrant corriendo
docker ps | grep qdrant

# Si no está, iniciar
docker-compose up -d qdrant
```

---

## 📞 Soporte

Para dudas específicas de implementación, consultar:
- `/workspace/docs/TOOL_USE_IMPLEMENTATION.md` - Guía completa
- `/workspace/docs/agent_swarm_architecture.md` - Arquitectura Swarm
- `/workspace/CLAUDE.md` - Contexto general del proyecto
