"""
Endpoints de Agentes — HERMES y MYSTIC
Cada llamada está aislada por tenant (RLS activo)
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.core.deps import AuthUser
from app.core.database import get_tenant_session
from app.agents.hermes import HermesAgent
from app.agents.mystic import MysticAgent

router = APIRouter()


class AgentMessage(BaseModel):
    conversation_id: Optional[UUID] = None
    message: str
    channel: str = "api"  # api | telegram | whatsapp


class AgentResponse(BaseModel):
    agent: str
    response: str
    conversation_id: UUID
    tokens_used: int


@router.post("/hermes/chat", response_model=AgentResponse)
async def hermes_chat(
    body: AgentMessage,
    current_user: AuthUser,
    background_tasks: BackgroundTasks,
):
    """HERMES: Orquestador de luz — responde, coordina, ejecuta."""
    async with get_tenant_session(current_user.tenant_id) as db:
        agent = HermesAgent(tenant_id=current_user.tenant_id, db=db)
        result = await agent.chat(
            message=body.message,
            conversation_id=body.conversation_id,
            user_id=current_user.user_id,
            channel=body.channel,
        )
        # Audit en background (no bloquea respuesta)
        background_tasks.add_task(
            agent.log_interaction,
            user_id=current_user.user_id,
            conversation_id=result["conversation_id"],
        )
        return AgentResponse(**result)


@router.post("/mystic/analyze", response_model=AgentResponse)
async def mystic_analyze(
    body: AgentMessage,
    current_user: AuthUser,
):
    """MYSTIC: Estratega de sombra — analiza, detecta, advierte."""
    async with get_tenant_session(current_user.tenant_id) as db:
        agent = MysticAgent(tenant_id=current_user.tenant_id, db=db)
        result = await agent.analyze(
            message=body.message,
            conversation_id=body.conversation_id,
            user_id=current_user.user_id,
        )
        return AgentResponse(**result)


@router.get("/status")
async def agents_status(current_user: AuthUser):
    """Estado de los agentes para el tenant."""
    return {
        "hermes": {"status": "active", "model": "claude-opus-4-6", "role": "orchestrator"},
        "mystic": {"status": "active", "model": "claude-sonnet-4-6", "role": "shadow_analyst"},
        "tenant_id": str(current_user.tenant_id),
    }
