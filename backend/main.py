"""
MYSTIC AI Operating System — REST API
Expone el orquestador de agentes como servicio HTTP.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Asegurar que el root del proyecto esté en el path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from orchestrator.orchestrator import Orchestrator
from memory.task_history import TaskHistory
from memory.knowledge_store import KnowledgeStore
from memory.vector_memory import VectorMemory


# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

CONFIGS_DIR = ROOT / "configs"
DATA_DIR = ROOT / ".data"
DATA_DIR.mkdir(exist_ok=True)

orchestrator: Orchestrator = None  # inicializado en lifespan


@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator
    orchestrator = Orchestrator.from_config(
        agents_config=str(CONFIGS_DIR / "agents.yaml"),
        skills_config=str(CONFIGS_DIR / "skills.yaml"),
    )
    orchestrator.task_history = TaskHistory(persist_path=str(DATA_DIR / "tasks.json"))
    orchestrator.knowledge_store = KnowledgeStore(persist_path=str(DATA_DIR / "knowledge.json"))
    yield


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="MYSTIC AI Operating System",
    description="Orquestador de agentes IA para Sonora Digital Corp",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TaskPayload(BaseModel):
    skill: str
    args: dict[str, Any] = Field(default_factory=dict)


class TaskRequest(BaseModel):
    id: str | None = None
    agent: str | None = None
    capability: str | None = None
    payload: TaskPayload


class SwarmRequest(BaseModel):
    tasks: list[TaskRequest]


class KnowledgePutRequest(BaseModel):
    key: str
    value: Any


class VectorAddRequest(BaseModel):
    key: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


# ---------------------------------------------------------------------------
# Rutas — Sistema
# ---------------------------------------------------------------------------

@app.get("/", tags=["sistema"])
def root():
    return {"system": "MYSTIC AI OS", "version": "1.0.0", "status": "running"}


@app.get("/status", tags=["sistema"])
def status():
    return orchestrator.status()


@app.get("/agents", tags=["sistema"])
def list_agents():
    return [
        {
            "name": a.name,
            "role": a.instance.role,
            "capabilities": a.capabilities,
            "skills": a.instance.list_skills(),
        }
        for a in orchestrator.agent_registry.list_agents()
    ]


@app.get("/skills", tags=["sistema"])
def list_skills():
    return [
        {"name": s.name, "description": s.description}
        for s in orchestrator.skill_registry.list_skills()
    ]


# ---------------------------------------------------------------------------
# Rutas — Ejecución de Tareas
# ---------------------------------------------------------------------------

@app.post("/task", tags=["tareas"])
def execute_task(req: TaskRequest):
    """Ejecuta una tarea en el agente correspondiente."""
    task = req.model_dump(exclude_none=True)
    task["payload"] = req.payload.model_dump()
    try:
        result = orchestrator.execute_task(task)
        return result
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error interno: {exc}")


@app.post("/swarm", tags=["tareas"])
def execute_swarm(req: SwarmRequest):
    """Ejecuta múltiples tareas en secuencia (swarm)."""
    tasks = [
        {**t.model_dump(exclude_none=True), "payload": t.payload.model_dump()}
        for t in req.tasks
    ]
    try:
        results = orchestrator.execute_swarm(tasks)
        return {"total": len(results), "results": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Rutas — Memoria
# ---------------------------------------------------------------------------

@app.get("/memory/tasks", tags=["memoria"])
def get_recent_tasks(limit: int = 10):
    records = orchestrator.task_history.recent(limit)
    return [
        {"task_id": r.task_id, "task": r.task, "result": r.result, "timestamp": r.timestamp}
        for r in records
    ]


@app.get("/memory/knowledge", tags=["memoria"])
def list_knowledge():
    return {"keys": orchestrator.knowledge_store.keys()}


@app.get("/memory/knowledge/{key}", tags=["memoria"])
def get_knowledge(key: str):
    value = orchestrator.knowledge_store.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Clave '{key}' no encontrada")
    return {"key": key, "value": value}


@app.post("/memory/knowledge", tags=["memoria"])
def put_knowledge(req: KnowledgePutRequest):
    orchestrator.knowledge_store.put(req.key, req.value)
    return {"status": "ok", "key": req.key}


@app.delete("/memory/knowledge/{key}", tags=["memoria"])
def delete_knowledge(key: str):
    deleted = orchestrator.knowledge_store.delete(key)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Clave '{key}' no encontrada")
    return {"status": "deleted", "key": key}


@app.post("/memory/knowledge/search", tags=["memoria"])
def search_knowledge(req: SearchRequest):
    results = orchestrator.knowledge_store.search(req.query)
    return {"query": req.query, "results": results}


# ---------------------------------------------------------------------------
# Rutas — Memoria Vectorial
# ---------------------------------------------------------------------------

_vector_memory: VectorMemory | None = None


def get_vector_memory() -> VectorMemory:
    global _vector_memory
    if _vector_memory is None:
        _vector_memory = VectorMemory(persist_path=str(DATA_DIR / "vectors.json"))
    return _vector_memory


@app.post("/memory/vectors", tags=["vectores"])
def add_vector(req: VectorAddRequest):
    vm = get_vector_memory()
    vm.add(req.key, req.text, metadata=req.metadata)
    return {"status": "ok", "key": req.key}


@app.post("/memory/vectors/search", tags=["vectores"])
def search_vectors(req: SearchRequest):
    vm = get_vector_memory()
    results = vm.similarity_search(req.query, limit=req.limit)
    return {
        "query": req.query,
        "results": [{"key": r.key, "text": r.text, "metadata": r.metadata} for r in results],
    }


# ---------------------------------------------------------------------------
# Manejo global de errores
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__},
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
