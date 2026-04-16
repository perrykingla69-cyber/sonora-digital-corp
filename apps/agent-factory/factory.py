"""
Agent Factory — Lógica de creación de agentes.
Genera código, Dockerfile, y despliega el contenedor.
"""

import asyncio
import logging
import os
import shutil
import tempfile
import uuid
from pathlib import Path

import asyncpg
import docker
import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL", "")
FACTORIES_DIR = Path(os.getenv("FACTORIES_DIR", "/app/factories"))
DOMAIN = os.getenv("DOMAIN", "sonoradigitalcorp.com")
MAX_CONCURRENT = int(os.getenv("AGENT_FACTORY_MAX_CONCURRENT", "5"))
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")


# ── Semaphore para límite de deploys simultáneos ──────────────
_deploy_semaphore = asyncio.Semaphore(MAX_CONCURRENT)


class CreateAgentBody(BaseModel):
    agent_id: str
    tenant_id: str
    name: str
    description: str
    verticales: list[str] = []
    agent_type: str = "chat"
    channel: str = "telegram"
    model: str = "gemini-flash"
    config: dict = {}


@router.post("/create", status_code=202)
async def create_agent(body: CreateAgentBody, background_tasks: BackgroundTasks):
    """Recibe request de hermes-api y lanza deploy en background."""
    background_tasks.add_task(_deploy_agent, body)
    return {"agent_id": body.agent_id, "status": "deploying"}


async def _deploy_agent(body: CreateAgentBody):
    """Pipeline completo: generar código → Dockerfile → deploy."""
    async with _deploy_semaphore:
        await _update_progress(body.agent_id, 5, "creating")
        try:
            # 1. Seleccionar template
            template_path = _get_template(body.agent_type)
            await _update_progress(body.agent_id, 20)

            # 2. Generar código del agente
            agent_code = _render_template(template_path, body)
            await _update_progress(body.agent_id, 40)

            # 3. Crear Dockerfile
            dockerfile_content = _generate_dockerfile(body)
            await _update_progress(body.agent_id, 55)

            # 4. Build + deploy
            container_id, deployment_url = await _docker_deploy(
                body.agent_id,
                body.tenant_id,
                agent_code,
                dockerfile_content,
                body,
            )
            await _update_progress(body.agent_id, 90)

            # 5. Marcar activo
            await _set_active(body.agent_id, container_id, deployment_url)
            await _update_progress(body.agent_id, 100, "active")
            logger.info(f"Agente {body.agent_id} desplegado: {deployment_url}")

        except Exception as e:
            logger.error(f"Error deploy agente {body.agent_id}: {e}", exc_info=True)
            await _set_failed(body.agent_id, str(e))


def _get_template(agent_type: str) -> Path:
    mapping = {
        "chat": "chat-agent.template.py",
        "task": "task-agent.template.py",
        "data-processor": "data-processor.template.py",
        "webhook": "webhook-agent.template.py",
    }
    filename = mapping.get(agent_type, "chat-agent.template.py")
    path = FACTORIES_DIR / filename
    if not path.exists():
        # Fallback al chat template
        path = FACTORIES_DIR / "chat-agent.template.py"
    return path


def _render_template(template_path: Path, body: CreateAgentBody) -> str:
    try:
        template = template_path.read_text()
    except FileNotFoundError:
        template = _default_chat_template()

    return template.replace("{{AGENT_NAME}}", body.name) \
                   .replace("{{AGENT_DESCRIPTION}}", body.description) \
                   .replace("{{AGENT_TYPE}}", body.agent_type) \
                   .replace("{{VERTICALES}}", ", ".join(body.verticales)) \
                   .replace("{{MODEL}}", body.model) \
                   .replace("{{CHANNEL}}", body.channel) \
                   .replace("{{AGENT_ID}}", body.agent_id) \
                   .replace("{{TENANT_ID}}", body.tenant_id)


def _generate_dockerfile(body: CreateAgentBody) -> str:
    return f"""FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn httpx openai

COPY agent.py .

ENV AGENT_ID="{body.agent_id}"
ENV TENANT_ID="{body.tenant_id}"
ENV AGENT_NAME="{body.name}"
ENV MODEL="{body.model}"
ENV OPENROUTER_API_KEY=""
ENV GOOGLE_API_KEY=""

EXPOSE 8080

CMD ["uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "8080"]
"""


async def _docker_deploy(
    agent_id: str,
    tenant_id: str,
    agent_code: str,
    dockerfile: str,
    body: CreateAgentBody,
) -> tuple[str, str]:
    """Build imagen Docker y lanza contenedor."""
    container_name = f"agent-{agent_id[:8]}"
    short_id = agent_id[:8]
    deployment_url = f"https://agent-{short_id}.{DOMAIN}"

    try:
        client = docker.from_env()
    except Exception:
        # Docker no disponible (CI/test) — simular deploy
        logger.warning("Docker no disponible — deploy simulado")
        await asyncio.sleep(2)
        return f"mock-{agent_id[:8]}", deployment_url

    # Crear directorio temporal con los archivos
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "agent.py").write_text(agent_code)
        (tmp / "Dockerfile").write_text(dockerfile)

        try:
            # Build imagen
            image, _ = client.images.build(
                path=str(tmp),
                tag=f"hermes-agent-{short_id}:latest",
                rm=True,
            )

            # Lanzar contenedor
            container = client.containers.run(
                image.id,
                name=container_name,
                detach=True,
                environment={
                    "AGENT_ID": agent_id,
                    "TENANT_ID": tenant_id,
                    "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
                    "GOOGLE_API_KEY": GOOGLE_API_KEY,
                },
                network="hermes_network",
                labels={
                    "hermes.agent_id": agent_id,
                    "hermes.tenant_id": tenant_id,
                    "hermes.managed": "true",
                },
                restart_policy={"Name": "unless-stopped"},
            )
            return container.id, deployment_url

        except docker.errors.BuildError as e:
            raise RuntimeError(f"Docker build failed: {e}")
        except docker.errors.APIError as e:
            raise RuntimeError(f"Docker API error: {e}")


# ── DB helpers ────────────────────────────────────────────────

async def _get_db_conn():
    dsn = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://") \
                      .replace("postgresql://", "postgresql://")
    return await asyncpg.connect(dsn)


async def _update_progress(agent_id: str, progress: int, status: str | None = None):
    try:
        conn = await _get_db_conn()
        try:
            if status:
                await conn.execute(
                    "UPDATE agent_deployments SET progress=$1, status=$2, updated_at=NOW() WHERE id=$3",
                    progress, status, uuid.UUID(agent_id),
                )
            else:
                await conn.execute(
                    "UPDATE agent_deployments SET progress=$1, updated_at=NOW() WHERE id=$2",
                    progress, uuid.UUID(agent_id),
                )
        finally:
            await conn.close()
    except Exception as e:
        logger.warning(f"No se pudo actualizar progreso: {e}")


async def _set_active(agent_id: str, container_id: str, deployment_url: str):
    try:
        conn = await _get_db_conn()
        try:
            await conn.execute(
                """UPDATE agent_deployments
                   SET status='active', progress=100, container_id=$1,
                       deployment_url=$2, updated_at=NOW()
                   WHERE id=$3""",
                container_id, deployment_url, uuid.UUID(agent_id),
            )
        finally:
            await conn.close()
    except Exception as e:
        logger.warning(f"No se pudo marcar activo: {e}")


async def _set_failed(agent_id: str, error: str):
    try:
        conn = await _get_db_conn()
        try:
            await conn.execute(
                """UPDATE agent_deployments
                   SET status='failed', error_message=$1, updated_at=NOW()
                   WHERE id=$2""",
                error[:1000], uuid.UUID(agent_id),
            )
        finally:
            await conn.close()
    except Exception as e:
        logger.warning(f"No se pudo marcar fallido: {e}")


def _default_chat_template() -> str:
    return '''"""
Agent: {{AGENT_NAME}}
Type: {{AGENT_TYPE}}
Description: {{AGENT_DESCRIPTION}}
"""

from fastapi import FastAPI
from pydantic import BaseModel
import httpx, os

app = FastAPI(title="{{AGENT_NAME}}")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "google/gemini-2.0-flash-001"


class ChatRequest(BaseModel):
    message: str
    user_id: str = ""


@app.post("/chat")
async def chat(body: ChatRequest):
    system_prompt = """Eres {{AGENT_NAME}}, un asistente especializado en {{VERTICALES}}.
{{AGENT_DESCRIPTION}}
Responde siempre en español de manera profesional y concisa."""

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": body.message},
                ],
                "max_tokens": 500,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        reply = data["choices"][0]["message"]["content"]

    return {"reply": reply, "agent": "{{AGENT_NAME}}"}


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "{{AGENT_NAME}}"}
'''
