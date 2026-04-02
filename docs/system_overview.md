# System Overview — MYSTIC AI Operating System

## ¿Qué es esto?

MYSTIC es un sistema operativo de IA que coordina agentes especializados para ejecutar
tareas de negocio, desarrollo, infraestructura e investigación. Está construido sobre
principios de soberanía digital (90% open source) y arquitectura modular.

## Capas del Sistema

```
┌─────────────────────────────────────────────┐
│              API REST (FastAPI)              │  ← Interfaz HTTP
├─────────────────────────────────────────────┤
│              Orquestador                    │  ← Coordinación central
├────────────┬────────────┬────────┬──────────┤
│ infra_agent│  dev_agent │knowled-│business_ │  ← Agentes de dominio
│            │            │ge_agent│agent     │
├────────────┴────────────┴────────┴──────────┤
│  filesystem │ shell │ github │ web │analysis│  ← Skills reales
├─────────────────────────────────────────────┤
│    TaskHistory │ KnowledgeStore │ VectorMem │  ← Memoria persistente
└─────────────────────────────────────────────┘
```

## Flujo de una Tarea

1. Cliente envía `POST /task` con payload JSON
2. Orquestador enruta al agente correcto (por nombre o capacidad)
3. Agente ejecuta el skill solicitado
4. Resultado se persiste en `TaskHistory`
5. Respuesta retorna al cliente con `status`, `result` y metadatos

## Tecnologías

| Componente | Tecnología | Costo |
|---|---|---|
| API | FastAPI + Python 3.10 | $0 |
| Agentes | Python puro | $0 |
| Búsqueda web | DuckDuckGo (sin API key) | $0 |
| LLM local | Ollama phi3:mini | $0 |
| Memoria | JSON / pgvector | $0 |
| GitHub | gh CLI | $0 |
| LLM externo | Claude API | Solo 5% queries |

## Archivos Clave

| Archivo | Propósito |
|---|---|
| `orchestrator/orchestrator.py` | Coordinación central |
| `agents/base_agent.py` | Clase base de todos los agentes |
| `skills/base_skill.py` | Interfaz estándar de todos los skills |
| `configs/agents.yaml` | Declaración de agentes y capacidades |
| `configs/skills.yaml` | Declaración de skills disponibles |
| `scripts/start_system.sh` | Arranque del sistema |
| `backend/main.py` | API REST expuesta al exterior |
