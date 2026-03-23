# 🏗️ MYSTIC - Arquitectura de Carpetas y Orquestación

## 📋 Estructura Maestra del Proyecto

```
sonora-digital-corp/
│
├── 📁 backend/                      # API Principal (FastAPI)
│   ├── app/                         # Código de la aplicación
│   │   ├── ai/                      # Inteligencia Artificial
│   │   │   ├── agents/              # Agentes especializados
│   │   │   │   ├── business_agent/  # Agente de negocios
│   │   │   │   ├── dev_agent/       # Agente de desarrollo
│   │   │   │   ├── infra_agent/     # Agente de infraestructura
│   │   │   │   └── knowledge_agent/ # Agente de conocimiento
│   │   │   ├── orchestrator/        # Orquestador principal
│   │   │   │   ├── __init__.py
│   │   │   │   ├── orchestrator.py  # Lógica de orquestación
│   │   │   │   ├── agent_registry.py # Registro de agentes
│   │   │   │   └── skill_registry.py # Registro de skills
│   │   │   ├── swarm/               # Sistema Queen-Worker
│   │   │   │   ├── __init__.py
│   │   │   │   ├── queen.py         # Queen Agent (coordinador)
│   │   │   │   └── workers.py       # Workers especializados
│   │   │   ├── tools/               # Herramientas tipo LangChain
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py          # BaseTool + Tools fiscales
│   │   │   │   └── tool_use.py      # Detección y ejecución
│   │   │   ├── rag/                 # Retrieval Augmented Generation
│   │   │   │   ├── __init__.py
│   │   │   │   ├── indexer.py       # Indexado en Qdrant
│   │   │   │   ├── retriever.py     # Búsqueda semántica
│   │   │   │   └── reranker.py      # Re-ranking (pendiente)
│   │   │   ├── embeddings/          # Modelos de embeddings
│   │   │   └── memory/              # Memoria conversacional
│   │   ├── api/                     # Endpoints API
│   │   │   ├── v1/                  # Versión 1 de endpoints
│   │   │   └── v2/                  # Versión 2 de endpoints
│   │   ├── core/                    # Configuración central
│   │   │   ├── config.py            # Variables de entorno
│   │   │   ├── security.py          # JWT, autenticación
│   │   │   └── logging.py           # Logging configurado
│   │   ├── db/                      # Base de datos
│   │   │   ├── session.py           # Sesiones PostgreSQL
│   │   │   ├── crud/                # Operaciones CRUD
│   │   │   └── models/              # Modelos SQLAlchemy
│   │   ├── middleware/              # Middleware FastAPI
│   │   │   ├── __init__.py
│   │   │   ├── metrics.py           # Métricas y telemetría
│   │   │   ├── security.py          # Rate limiting, CORS
│   │   │   └── auth.py              # Autenticación JWT
│   │   ├── services/                # Servicios externos
│   │   │   ├── sat.py               # Consulta SAT
│   │   │   ├── n8n.py               # Trigger workflows N8N
│   │   │   ├── qdrant.py            # Cliente Qdrant
│   │   │   └── ollama.py            # Cliente Ollama
│   │   └── utils/                   # Utilidades generales
│   ├── main.py                      # Entry point FastAPI ⭐
│   ├── requirements.txt             # Dependencias Python
│   ├── Dockerfile                   # Contenedor backend
│   └── schemas.py                   # Pydantic schemas
│
├── 📁 apps/                         # Aplicaciones independientes
│   ├── api/                         # API adicional (si existe)
│   ├── bot/                         # Telegram Bot
│   │   ├── mystic_bot.py
│   │   └── requirements.txt
│   ├── cli/                         # CLI propia (en desarrollo)
│   │   ├── main.py
│   │   └── commands/
│   ├── frontend/                    # Next.js Dashboard
│   │   ├── src/
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   └── styles/
│   │   ├── public/
│   │   └── package.json
│   ├── mcp-server/                  # MCP Server ⭐ NUEVO
│   │   └── server.py                # 8 herramientas fiscales
│   └── whatsapp/                    # WhatsApp Bot (Baileys)
│       └── server.js
│
├── 📁 scripts/                      # Scripts de automatización
│   ├── data_ingestor.py             # Ingesta multi-fuente ⭐
│   ├── optimize_ram.sh              # Optimización memoria ⭐
│   ├── seed_*.py                    # Scripts de sembrado
│   │   ├── seed_fourgea_docs.py
│   │   ├── seed_knowledge.py
│   │   ├── seed_legal_mve.py
│   │   └── seed_qdrant.py
│   ├── migrate_*.py                 # Migraciones
│   ├── mystic_monitor.sh            # Monitoreo sistema
│   └── setup_rag.sh                 # Setup RAG
│
├── 📁 infra/                        # Infraestructura
│   ├── docker-compose.yml           # Docker local
│   ├── docker-compose.vps.yml       # Docker VPS ⭐
│   ├── nginx/                       # Configuración Nginx
│   │   └── nginx.conf
│   ├── database/                    # Scripts DB
│   ├── monitoring/                  # Prometheus, Grafana
│   └── n8n-workflows/               # Workflows N8N ⭐
│       ├── Alerta_Vencimientos_SAT.json
│       ├── Clasificacion_Arancelaria_WA.json
│       ├── Pedimento_Calculo_WA.json
│       └── ... (12 workflows)
│
├── 📁 packages/                     # Paquetes compartidos (monorepo)
│   ├── agent-runtime/               # Runtime de agentes
│   ├── evals/                       # Evaluaciones
│   ├── memory/                      # Memoria compartida
│   ├── shared-types/                # Tipos TypeScript/Python
│   ├── skills/                      # Skills library
│   └── workflow-runtime/            # Runtime de workflows
│
├── 📁 docs/                         # Documentación
│   ├── ARCHITECTURE.md              # Arquitectura general
│   ├── TOOL_USE_IMPLEMENTATION.md   # Tool Use ⭐
│   ├── CLAUDE_COMMANDS.md           # Comandos copy-paste ⭐
│   ├── SECURITY_INGESTION_GUIDE.md  # Guía seguridad ⭐
│   ├── DEPLOY_COMMANDS.md           # Deploy en VPS
│   ├── system_overview.md           # Vista del sistema
│   └── decisions/                   # Decisiones de diseño
│
├── 📁 tests/                        # Pruebas automatizadas
│   ├── test_api.py
│   ├── test_skills.py
│   ├── test_agent_runtime_v2.py
│   └── ...
│
├── 📁 workflows/                    # Workflows adicionales
│   ├── n8n/                         # Workflows N8N extra
│   └── catalogs/                    # Catálogos fiscales
│
├── 📁 bot/                          # Bot legacy (mover a apps/)
│   ├── mystic_bot.py
│   └── requirements.txt
│
├── 📁 whatsapp/                     # WhatsApp legacy (mover a apps/)
│   └── server.js
│
├── 📁 frontend/                     # Frontend legacy (mover a apps/)
│   └── ...
│
├── README.md                        # Documentación principal
├── CLAUDE.md                        # Instrucciones para Claude
├── Makefile                         # Comandos make
└── .env                             # Variables de entorno (NO COMMIT)
```

---

## 🔄 Flujo de Datos y Orquestación

### 1. **Entrada de Usuario** (WhatsApp / Telegram / API)
```
Usuario → WhatsApp/Telegram → apps/whatsapp/server.js o apps/bot/mystic_bot.py
                              ↓
                         POST /api/brain/ask
                              ↓
                        backend/main.py
```

### 2. **Procesamiento en el Brain** (`backend/main.py` línea ~2333)
```
/api/brain/ask
    ↓
[1] Redis Cache → ¿Ya respondí esto? → Sí: Retorna cache
    ↓ No
[2] Tool Use Detection → ¿Necesita ejecutar acción?
    ↓ Sí (confianza > 0.7)
    → Orchestrator.execute_task(tool_name, args)
        → apps/mcp-server/server.py (herramientas)
        → n8n_trigger, sat_query, database_query, rag_index
    ↓ No (pregunta normal)
[3] RAG Pipeline:
    → Qdrant (búsqueda semántica)
    → Fallback: PostgreSQL full-text
    → Direct RAG: ¿Respuesta literal en docs? → Sí: Retorna
    ↓ No
[4] Ollama (DeepSeek R1) → Sintetiza con contexto
    ↓ Fallback
[5] Retorna RAG crudo si Ollama falla
```

### 3. **Sistema Swarm Queen-Worker** (`/api/brain/swarm`)
```
QueenAgent (queen.py)
    ↓ Decide qué workers activar
    ├─→ WorkerFacturas (CFDI, XML, ingresos)
    ├─→ WorkerNomina (IMSS, ISR, empleados)
    └─→ WorkerIVA (IVA, DIOT, SAT)
    ↓ Ejecuta en paralelo
    ↓ Consolida respuestas
    ↓ Retorna al usuario
```

### 4. **MCP Server** (`apps/mcp-server/server.py`) ⭐ NUEVO
```
Herramientas disponibles (8):
├─ calcular_isr(ingresos, deducciones)
├─ calcular_iva(monto, tasa)
├─ calcular_pedimento(fraccion, valor_usd, ...)
├─ calcular_nomina(empleado, periodo)
├─ consultar_imss(rfc)
├─ buscar_qdrant(query, tenant)
├─ calendario_sat(mes, año)
└─ estado_sistema()

El Brain llama automáticamente cuando detecta intención.
```

### 5. **Data Ingestion** (`scripts/data_ingestor.py`) ⭐ NUEVO
```
Fuentes soportadas:
├─ Gmail (OAuth2) → Lee correos → Extrae CFDIs → Indexa en Qdrant
├─ Outlook (OAuth2) → Lee correos → Extrae facturas
├─ Dropbox → Sync carpetas → Procesa PDFs/XMLs
├─ Google Drive → Sync carpetas → Procesa documentos
├─ Local folders → Escanea directorios → Indexa
└─ DOF Scraper → Baja leyes → Embeddings → Qdrant

Comando:
python3 scripts/data_ingestor.py add gmail --tenant fourgea --email nathaly@fourgea.com
```

### 6. **Workflows N8N Automatizados** (12 activos)
```
Triggers:
├─ Cron: Alerta SAT (días 10,14,16,17 a las 8am)
├─ Cron: Reporte Ejecutivo (Lunes 8am)
├─ Cron: Scorecard Semanal (Lunes 9am)
├─ Cron: DOF Auto-Seed (Lunes 7am) ⭐ NUEVO
├─ Webhook: Cierre Mensual
├─ Webhook: Factura Nueva
├─ Webhook: Clasificación Arancelaria
├─ Webhook: Pedimento Cálculo
└─ Webhook: Onboarding Complete

Todos disparan acciones en backend vía HTTP.
```

---

## 🚀 Comandos Clave por Capa

### **Capa 1: Infraestructura**
```bash
# VPS: Reiniciar todo el sistema
cd /home/mystic/sonora-digital-corp/infra
docker compose -f docker-compose.vps.yml up -d

# Ver logs en tiempo real
docker logs -f mystic-backend-1
docker logs -f mystic-n8n-1

# Optimizar RAM
./scripts/optimize_ram.sh
```

### **Capa 2: Backend API**
```bash
# Local: Iniciar backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Probar endpoint Brain
curl -X POST http://localhost:8000/api/brain/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuánto ISR pago con $50,000 de ingresos?", "tenant": "fourgea"}'

# Probar Tool Use
curl -X POST http://localhost:8000/api/brain/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Ejecuta el cierre mensual de Fourgea", "tenant": "fourgea"}'
```

### **Capa 3: Data Ingestion**
```bash
# Agregar fuente de datos
python3 scripts/data_ingestor.py add gmail \
  --tenant fourgea \
  --email nathaly@fourgea.com \
  --scopes read_mail

# Listar fuentes conectadas
python3 scripts/data_ingestor.py list --tenant fourgea

# Forzar sync manual
python3 scripts/data_ingestor.py sync --tenant fourgea --source gmail
```

### **Capa 4: MCP Server**
```bash
# Probar MCP Server standalone
python3 apps/mcp-server/server.py

# Registrar en Claude Code
claude mcp add mystic-fiscal -- python3 /workspace/apps/mcp-server/server.py

# Ver herramientas disponibles
claude mcp list
```

### **Capa 5: Seed RAG**
```bash
# Sembrar docs fiscales completos
python3 scripts/seed_fiscal_completo.py

# Sembrar datos específicos de Fourgea
python3 scripts/seed_fourgea_docs.py

# Sembrar leyes del DOF automáticamente (semanal)
# Ya está automatizado vía N8N: DOF_Auto_Seed_Semanal.json
```

---

## 🔐 Seguridad y Permisos

### **Estructura de Tenants**
```
Cada tenant tiene:
├─ Colección Qdrant separada (qdrant_collection=fourgea_docs)
├─ Tablas PostgreSQL con tenant_id
├─ Credenciales N8N aisladas
└─ Variables de entorno por tenant

Flujo:
Usuario (Nathaly) → WhatsApp → Detecta tenant por número → 
Filtra queries por tenant_id → Retorna solo datos de Fourgea
```

### **Variables de Entorno Críticas** (`.env`)
```bash
# Database
DATABASE_URL=postgresql://mystic:SECRET_PASSWORD@postgres:5432/mystic_db

# Qdrant
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=secret_key

# Ollama
OLLAMA_HOST=http://ollama:11434

# N8N
N8N_BASE_URL=http://n8n:5678
N8N_WEBHOOK_SECRET=webhook_secret_key

# WhatsApp
WHATSAPP_SESSION_PATH=./whatsapp_session.json

# MCP Server
MCP_SERVER_PORT=8765

# Tenant isolation
DEFAULT_TENANT=fourgea
TENANT_ISOLATION=true
```

---

## 📊 Estado Actual vs Pendiente

| Componente | Estado | Ubicación | Prioridad |
|------------|--------|-----------|-----------|
| Brain RAG 4 capas | ✅ Producción | `backend/main.py` | Alta |
| Swarm Queen-Worker | ✅ Producción | `backend/app/ai/swarm/` | Alta |
| Tool Use Detection | ✅ Implementado | `backend/app/ai/tools/` | Alta |
| MCP Server 8 herramientas | ✅ Implementado | `apps/mcp-server/` | Media |
| Data Ingestor Multi-fuente | ✅ Implementado | `scripts/data_ingestor.py` | Alta |
| Optimize RAM Script | ✅ Implementado | `scripts/optimize_ram.sh` | Media |
| 12 Workflows N8N | ✅ Producción | `infra/n8n-workflows/` | Alta |
| WhatsApp Bot | ✅ Producción | `apps/whatsapp/` | Alta |
| Telegram Bot | ✅ Producción | `apps/bot/` | Media |
| RAG per-tenant sembrado | ⚠️ Vacío | Qdrant collections | **CRÍTICO** |
| Agents 5-8 conectados | ⚠️ Stubs | `backend/app/ai/agents/` | Media |
| Frontend Dashboard | ⚠️ Básico | `apps/frontend/` | Baja |
| CLI propia | ❌ No existe | `apps/cli/` | Baja |
| Skills 2.5 contrato | ❌ No existe | `packages/skills/` | Baja |

---

## 🎯 Próximos Pasos (Orden de Ejecución)

### **Semana 1: Poblar RAG con datos reales**
1. `python3 scripts/data_ingestor.py add gmail --tenant fourgea --email nathaly@fourgea.com`
2. `python3 scripts/seed_fourgea_docs.py`
3. Verificar en Qdrant: `curl http://localhost:6333/collections/fourgea_docs/points/count`

### **Semana 2: Conectar Tool Use al Brain**
1. Modificar `backend/main.py` línea ~2333 para integrar `detect_tool_calls()`
2. Probar: `curl -X POST /api/brain/ask` con comando de acción
3. Verificar que ejecute N8N workflow

### **Semana 3: Dashboard Frontend**
1. Agregar tarjetas de métricas en `apps/frontend/src/pages/dashboard.tsx`
2. Conectar a `/api/metrics`
3. Agregar vista de Tool Use executions

### **Semana 4: Agents 5-8 con lógica real**
1. Implementar `KnowledgeAgent` para búsquedas avanzadas
2. Implementar `BusinessAgent` para reportes ejecutivos
3. Conectar al Orchestrator

---

## 📞 Soporte y Debugging

### **Logs por componente**
```bash
# Backend
docker logs -f mystic-backend-1 | grep "ERROR\|TOOL_USE"

# N8N
docker logs -f mystic-n8n-1 | grep "Workflow\|Error"

# Qdrant
docker logs -f mystic-qdrant-1

# Ollama
docker logs -f mystic-ollama-1 | grep "model\|error"
```

### **Health Checks**
```bash
# API
curl http://localhost:8000/api/health

# Metrics
curl http://localhost:8000/api/metrics

# Qdrant
curl http://localhost:6333/collections

# Ollama
curl http://localhost:11434/api/tags
```

---

**Esta es tu arquitectura completa.** Cada carpeta tiene un propósito claro y todos los componentes están interconectados. El flujo principal es: **Usuario → Bot → Brain → [Tool Use o RAG] → Respuesta/Acción**.
