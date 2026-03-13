# Arquitectura del Enjambre de Agentes

## Agentes Disponibles

### infra_agent
- **Rol:** Operaciones de infraestructura, despliegue y confiabilidad
- **Capacidades:** infrastructure, deployment, observability, monitoring
- **Skills:** shell, filesystem, analysis
- **Casos de uso:** correr comandos en servidor, revisar logs, verificar servicios Docker, deployar

### dev_agent
- **Rol:** Desarrollo de software, generación de código e integración
- **Capacidades:** software_development, code_generation, testing, refactoring
- **Skills:** filesystem, shell, github, analysis
- **Casos de uso:** crear/editar archivos, correr tests, crear PRs, analizar código

### knowledge_agent
- **Rol:** Investigación, síntesis y recuperación de conocimiento
- **Capacidades:** documentation, knowledge_retrieval, summarization, research
- **Skills:** web_search, analysis, filesystem
- **Casos de uso:** buscar información, resumir documentos, investigar tecnologías

### business_agent
- **Rol:** Estrategia, planeación, análisis de mercado y reportes
- **Capacidades:** planning, market_analysis, reporting, strategy
- **Skills:** web_search, analysis, github, filesystem
- **Casos de uso:** generar reportes, analizar competencia, crear propuestas

## Modelo de Interacción

```
Cliente / API
     │
     ▼
Orchestrator.execute_task(task)
     │
     ├── TaskRouter.route(task)
     │       ├── por "agent" explícito
     │       ├── por "capability"
     │       └── fallback: primer agente
     │
     ▼
BaseAgent.__call__(payload)
     │
     └── BaseAgent.run_skill(skill_name, **args)
             │
             └── Skill.__call__(**args)
                     │
                     └── Skill.execute(**args) → resultado real
```

## Ejecución en Enjambre

Para tareas multi-dominio se usa `execute_swarm()`:

```python
results = orchestrator.execute_swarm([
    {"agent": "knowledge_agent", "payload": {"skill": "web_search", "args": {...}}},
    {"agent": "dev_agent",       "payload": {"skill": "filesystem",  "args": {...}}},
    {"agent": "infra_agent",     "payload": {"skill": "shell",       "args": {...}}},
])
```

**Estado actual:** ejecución secuencial.
**Próximo paso:** paralelización con `asyncio.gather()` o `ThreadPoolExecutor`.

## Agregar un Agente Nuevo

1. Crear `agents/mi_agente/config.yaml` con `name`, `role`, `capabilities`, `skills`
2. Crear `agents/mi_agente/agent.py` importando `BaseAgent`
3. Agregar entrada en `configs/agents.yaml`
4. El orquestador lo carga automáticamente en el siguiente arranque

## Agregar un Skill Nuevo

1. Crear `skills/mi_skill/skill.py` heredando `BaseSkill` e implementando `execute()`
2. Crear `skills/mi_skill/__init__.py` con `run = lambda **kw: Skill()(**kw)`
3. Agregar entrada en `configs/skills.yaml`
4. Agregar el skill a los agentes que lo necesiten en sus `config.yaml`
