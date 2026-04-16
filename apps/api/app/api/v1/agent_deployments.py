"""
Agent Deployments — CRUD + factory trigger
Crea agentes IA y los registra en agent_deployments.
"""

import httpx
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import text
import os

from app.core.database import get_tenant_session
from app.core.deps import AuthUser

logger = logging.getLogger(__name__)
router = APIRouter()

AGENT_FACTORY_URL = os.getenv("AGENT_FACTORY_URL", "http://agent-factory:8000")

PLAN_LIMITS = {
    "free": 1,
    "pro": 5,
    "enterprise": -1,  # unlimited
}


# ── Schemas ───────────────────────────────────────────────────

class CreateAgentRequest(BaseModel):
    name: str
    description: str
    verticales: list[str] = []
    agent_type: str = "chat"  # chat | task | data-processor | webhook
    channel: str = "telegram"  # telegram | whatsapp
    config: dict = {}


class AgentResponse(BaseModel):
    agent_id: str
    status: str
    estimated_time: str = "2-3 minutos"
    check_status_url: str


class AgentStatusResponse(BaseModel):
    id: str
    name: str
    status: str
    progress: int
    description: Optional[str] = None
    container_id: Optional[str] = None
    deployment_url: Optional[str] = None
    error: Optional[str] = None
    created_at: str


# ── Helpers ───────────────────────────────────────────────────

async def _check_agent_limit(db, user_id: str, plan: str) -> bool:
    limit = PLAN_LIMITS.get(plan, 1)
    if limit == -1:
        return True
    r = await db.execute(
        text("""
            SELECT COUNT(*) FROM agent_deployments
            WHERE user_id = :uid AND status NOT IN ('destroying', 'failed')
        """),
        {"uid": user_id},
    )
    count = r.scalar_one()
    return count < limit


async def _get_user_plan(db, user_id: str) -> str:
    r = await db.execute(
        text("SELECT subscription_plan FROM users WHERE id = :uid"),
        {"uid": user_id},
    )
    row = r.fetchone()
    return row.subscription_plan if row else "free"


# ── Endpoints ─────────────────────────────────────────────────

@router.post("/create", response_model=AgentResponse, status_code=202)
async def create_agent(
    body: CreateAgentRequest,
    background_tasks: BackgroundTasks,
    current_user: AuthUser,
):
    """
    Crea un nuevo agente IA.
    Valida límites del plan, registra en DB, dispara Agent Factory en background.
    """
    # Validar tipo
    valid_types = {"chat", "task", "data-processor", "webhook"}
    if body.agent_type not in valid_types:
        raise HTTPException(400, f"agent_type inválido. Válidos: {valid_types}")

    async with get_tenant_session(current_user.tenant_id) as db:
        # Verificar límite del plan
        plan = await _get_user_plan(db, str(current_user.user_id))
        allowed = await _check_agent_limit(db, str(current_user.user_id), plan)
        if not allowed:
            raise HTTPException(
                403,
                f"Límite del plan '{plan}' alcanzado. "
                f"Máximo {PLAN_LIMITS.get(plan, 1)} agentes activos."
            )

        # Verificar nombre único en el tenant
        dup = await db.execute(
            text("""
                SELECT id FROM agent_deployments
                WHERE tenant_id = current_tenant_id() AND name = :name
            """),
            {"name": body.name},
        )
        if dup.fetchone():
            raise HTTPException(400, f"Ya existe un agente con el nombre '{body.name}'")

        # Seleccionar modelo
        model = _select_model(body.agent_type, body.verticales)

        # Crear registro en DB (status: creating)
        r = await db.execute(
            text("""
                INSERT INTO agent_deployments
                    (user_id, tenant_id, name, description, agent_type, model,
                     status, progress, verticales, config)
                VALUES
                    (:uid, current_tenant_id(), :name, :desc, :atype, :model,
                     'creating', 0, :verticales, :config)
                RETURNING id
            """),
            {
                "uid": str(current_user.user_id),
                "name": body.name,
                "desc": body.description,
                "atype": body.agent_type,
                "model": model,
                "verticales": body.verticales,
                "config": body.config,
            },
        )
        agent_id = r.scalar_one()

    # Disparar factory en background
    background_tasks.add_task(
        _trigger_agent_factory,
        str(agent_id),
        str(current_user.tenant_id),
        body,
        model,
    )

    return AgentResponse(
        agent_id=str(agent_id),
        status="creating",
        estimated_time="2-3 minutos",
        check_status_url=f"/api/v1/agents/{agent_id}/status",
    )


@router.get("/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(agent_id: str, current_user: AuthUser):
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("""
                SELECT id, name, description, status, progress,
                       container_id, deployment_url, error_message, created_at
                FROM agent_deployments
                WHERE id = :aid AND user_id = :uid
            """),
            {"aid": agent_id, "uid": str(current_user.user_id)},
        )
        row = r.fetchone()
    if not row:
        raise HTTPException(404, "Agente no encontrado")
    d = dict(row._mapping)
    return AgentStatusResponse(
        id=str(d["id"]),
        name=d["name"],
        status=d["status"],
        progress=d["progress"],
        description=d.get("description"),
        container_id=d.get("container_id"),
        deployment_url=d.get("deployment_url"),
        error=d.get("error_message"),
        created_at=d["created_at"].isoformat() if d.get("created_at") else "",
    )


@router.get("/")
async def list_agents(current_user: AuthUser):
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("""
                SELECT id, name, description, agent_type, model, status, progress,
                       deployment_url, created_at, updated_at
                FROM agent_deployments
                WHERE user_id = :uid
                ORDER BY created_at DESC
            """),
            {"uid": str(current_user.user_id)},
        )
        rows = r.fetchall()
    return [
        {k: str(v) if hasattr(v, 'hex') else
         v.isoformat() if hasattr(v, 'isoformat') else v
         for k, v in dict(row._mapping).items()}
        for row in rows
    ]


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, current_user: AuthUser):
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("""
                UPDATE agent_deployments
                SET status = 'destroying', updated_at = NOW()
                WHERE id = :aid AND user_id = :uid
                RETURNING id
            """),
            {"aid": agent_id, "uid": str(current_user.user_id)},
        )
        if not r.fetchone():
            raise HTTPException(404, "Agente no encontrado")
    return {"detail": "Agente marcado para eliminación"}


# ── Internal ──────────────────────────────────────────────────

def _select_model(agent_type: str, verticales: list[str]) -> str:
    """Selecciona el modelo óptimo según complejidad de la tarea."""
    complex_types = {"data-processor", "task"}
    complex_verticales = {"contador", "abogado", "fiscal"}
    if agent_type in complex_types or any(v in complex_verticales for v in verticales):
        return "claude-code"
    return "gemini-flash"


async def _trigger_agent_factory(
    agent_id: str,
    tenant_id: str,
    body: CreateAgentRequest,
    model: str,
):
    """Llama al Agent Factory service para crear el contenedor."""
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                f"{AGENT_FACTORY_URL}/factory/create",
                json={
                    "agent_id": agent_id,
                    "tenant_id": tenant_id,
                    "name": body.name,
                    "description": body.description,
                    "verticales": body.verticales,
                    "agent_type": body.agent_type,
                    "channel": body.channel,
                    "model": model,
                    "config": body.config,
                },
            )
            resp.raise_for_status()
    except Exception as e:
        logger.error(f"Agent factory error para {agent_id}: {e}")
        # Marcar como fallido en DB
        try:
            from app.core.database import get_tenant_session
            from uuid import UUID
            async with get_tenant_session(UUID(tenant_id)) as db:
                await db.execute(
                    text("""
                        UPDATE agent_deployments
                        SET status = 'failed', error_message = :err, updated_at = NOW()
                        WHERE id = :aid
                    """),
                    {"err": str(e), "aid": agent_id},
                )
        except Exception as db_err:
            logger.error(f"No se pudo actualizar estado fallido: {db_err}")
