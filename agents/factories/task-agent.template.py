"""
Agent: {{AGENT_NAME}}
Type: task
Description: {{AGENT_DESCRIPTION}}
Verticales: {{VERTICALES}}
Model: {{MODEL}}
"""

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import httpx
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="{{AGENT_NAME}}")

AGENT_ID = os.getenv("AGENT_ID", "{{AGENT_ID}}")
TENANT_ID = os.getenv("TENANT_ID", "{{TENANT_ID}}")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "google/gemini-2.0-flash-001"

# Para tareas complejas se puede escalar a Claude
COMPLEX_MODEL = "anthropic/claude-3-5-haiku"

TASK_PROMPT = """Eres {{AGENT_NAME}}, un agente ejecutor especializado en {{VERTICALES}}.

{{AGENT_DESCRIPTION}}

Tu rol es ejecutar tareas específicas de forma autónoma:
- Analiza la tarea completamente antes de actuar
- Divide tareas complejas en pasos
- Reporta progreso y resultado claramente
- Si encuentras un error, explica qué salió mal y por qué
"""

task_results: dict = {}


class TaskRequest(BaseModel):
    task: str
    parameters: dict = {}
    user_id: str = ""
    callback_url: str = ""


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskResult(BaseModel):
    task_id: str
    status: str  # pending | running | completed | failed
    result: str = ""
    error: str = ""


@app.post("/tasks", response_model=TaskResponse)
async def create_task(body: TaskRequest, background: BackgroundTasks):
    import uuid
    task_id = str(uuid.uuid4())
    task_results[task_id] = {"status": "pending", "result": "", "error": ""}
    background.add_task(_execute_task, task_id, body)
    return TaskResponse(task_id=task_id, status="pending", message="Tarea iniciada")


@app.get("/tasks/{task_id}", response_model=TaskResult)
async def get_task(task_id: str):
    if task_id not in task_results:
        from fastapi import HTTPException
        raise HTTPException(404, "Tarea no encontrada")
    r = task_results[task_id]
    return TaskResult(
        task_id=task_id,
        status=r["status"],
        result=r.get("result", ""),
        error=r.get("error", ""),
    )


async def _execute_task(task_id: str, body: TaskRequest):
    task_results[task_id]["status"] = "running"
    try:
        prompt = f"""Tarea: {body.task}

Parámetros: {body.parameters}

Ejecuta esta tarea y provee el resultado completo.
Si necesitas información adicional, explícalo.
Formato: resultado directo sin rodeos."""

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": TASK_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 1500,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        result = data["choices"][0]["message"]["content"]
        task_results[task_id]["status"] = "completed"
        task_results[task_id]["result"] = result

        # Callback si se proporcionó
        if body.callback_url:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    await client.post(body.callback_url, json={
                        "task_id": task_id,
                        "status": "completed",
                        "result": result,
                    })
            except Exception:
                pass

    except Exception as e:
        task_results[task_id]["status"] = "failed"
        task_results[task_id]["error"] = str(e)
        logger.error(f"Task {task_id} failed: {e}")


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "{{AGENT_NAME}}", "agent_id": AGENT_ID}
