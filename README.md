# MYSTIC AI Operating System

Orquestador de agentes IA para **Sonora Digital Corp** — arquitectura modular, soberana y open source.

## Estructura

```
sonora-digital-corp/
├── orchestrator/       ← Coordinación central (registry, router, ejecución)
├── agents/             ← 4 agentes de dominio + BaseAgent compartido
├── skills/             ← 5 skills reales con interfaz estándar
├── memory/             ← TaskHistory, KnowledgeStore, VectorMemory
├── backend/            ← REST API FastAPI (puerto 8002)
├── configs/            ← agents.yaml + skills.yaml
├── prompts/            ← Filosofía del enjambre + lógica de coordinación
├── docs/               ← Documentación de arquitectura y diseño
├── scripts/            ← start_system.sh
└── tests/              ← 26 pruebas (skills + API)
```

## Agentes

| Agente | Rol | Skills |
|---|---|---|
| `infra_agent` | Infraestructura y despliegue | shell, filesystem, analysis |
| `dev_agent` | Desarrollo y código | filesystem, shell, github, analysis |
| `knowledge_agent` | Investigación y síntesis | web_search, analysis, filesystem |
| `business_agent` | Estrategia y reportes | web_search, analysis, github, filesystem |

## Skills

| Skill | Qué hace |
|---|---|
| `filesystem` | Leer, escribir, listar y borrar archivos |
| `shell` | Ejecutar comandos bash (con bloqueo de comandos peligrosos) |
| `github` | Repos, PRs e issues via `gh` CLI |
| `web_search` | DuckDuckGo sin API key + fallback urllib |
| `analysis` | Stats, keywords, resumen (Ollama local o extractivo) |

## Inicio rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Arrancar y verificar sistema
bash scripts/start_system.sh

# Levantar API
python backend/main.py
# → http://localhost:8002/docs
```

## API REST

```bash
# Ejecutar una tarea
curl -X POST http://localhost:8002/task \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "dev_agent",
    "payload": {
      "skill": "shell",
      "args": {"command": "docker ps"}
    }
  }'

# Ejecutar enjambre
curl -X POST http://localhost:8002/swarm \
  -H "Content-Type: application/json" \
  -d '{"tasks": [...]}'

# Ver estado
curl http://localhost:8002/status

# Documentación interactiva
open http://localhost:8002/docs
```

## Endpoints disponibles

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/status` | Estado del orquestador |
| GET | `/agents` | Lista de agentes con capacidades |
| GET | `/skills` | Lista de skills disponibles |
| POST | `/task` | Ejecutar una tarea |
| POST | `/swarm` | Ejecutar múltiples tareas |
| GET | `/memory/tasks` | Historial de tareas recientes |
| GET/POST/DELETE | `/memory/knowledge/{key}` | CRUD de knowledge store |
| POST | `/memory/knowledge/search` | Búsqueda en knowledge store |
| POST | `/memory/vectors` | Agregar documento vectorial |
| POST | `/memory/vectors/search` | Búsqueda semántica |

## Tests

```bash
python -m pytest tests/ -v
# 26 passed
```

## Filosofía

- **90% open source** — sin dependencia de APIs de pago
- **Principio de Inversión de Inferencia**: determinístico → caché → Ollama local → Claude API (5%)
- **Memoria persistente**: cada tarea aprendida queda guardada
- **Degradación graceful**: skill o agente faltante → warning, no crash
