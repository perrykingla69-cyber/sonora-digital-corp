"""
Endpoints de Agentes — HERMES y MYSTIC
Cada llamada está aislada por tenant (RLS activo)
Autenticación JWT: valida tenant_id en payload
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from app.core.deps import AuthUser
from app.core.database import get_tenant_session
from app.agents.hermes import HermesAgent
from app.agents.mystic import MysticAgent

logger = logging.getLogger(__name__)
router = APIRouter()


# ========== REQUEST SCHEMAS ==========

class HermesChatRequest(BaseModel):
    """Request para HERMES chat endpoint."""
    message: str
    context: Optional[str] = None
    conversation_id: Optional[UUID] = None
    channel: str = "api"


class MysticAnalyzeRequest(BaseModel):
    """Request para MYSTIC analyze endpoint."""
    data: str
    analysis_type: str  # fiscal | food | legal
    conversation_id: Optional[UUID] = None


# ========== RESPONSE SCHEMAS ==========

class HermesChatResponse(BaseModel):
    """Response para HERMES chat endpoint."""
    response: str
    source: str  # rag | openrouter | cache
    tokens_used: int
    conversation_id: UUID


class MysticAnalyzeResponse(BaseModel):
    """Response para MYSTIC analyze endpoint."""
    analysis: str
    recommendations: List[str]
    risk_level: str  # 🔴 crítico | 🟡 advertencia | 🟢 ok


class ErrorResponse(BaseModel):
    """Response genérico para errores."""
    error: str
    code: int


# ========== ENDPOINTS ==========

@router.post(
    "/hermes/chat",
    response_model=HermesChatResponse,
    status_code=200,
    summary="Chat con HERMES",
    description="Envía un mensaje a HERMES para obtener respuesta con contexto RAG",
)
async def hermes_chat(
    body: HermesChatRequest,
    current_user: AuthUser,
    background_tasks: BackgroundTasks,
):
    """
    HERMES: Orquestador de luz — responde, coordina, ejecuta.

    - **message**: Pregunta del usuario
    - **context**: Contexto adicional (opcional)
    - **conversation_id**: ID de conversación existente (opcional)
    - **channel**: Canal (api | telegram | whatsapp, default: api)

    Retorna:
    - **response**: Respuesta de HERMES
    - **source**: Origen (rag | openrouter | cache)
    - **tokens_used**: Tokens consumidos
    - **conversation_id**: ID de conversación
    """
    try:
        async with get_tenant_session(current_user.tenant_id) as db:
            agent = HermesAgent(tenant_id=current_user.tenant_id, db=db)

            # Combinar contexto adicional si se proporciona
            message = body.message
            if body.context:
                message = f"{body.context}\n\n{body.message}"

            result = await agent.chat(
                message=message,
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

            # Determinar fuente (RAG, cache o OpenRouter)
            source = "openrouter"
            if result.get("cached"):
                source = "cache"
            # TODO: agregar field a HermesAgent.chat() para indicar si usó RAG

            return HermesChatResponse(
                response=result["response"],
                source=source,
                tokens_used=result["tokens_used"],
                conversation_id=result["conversation_id"],
            )

    except Exception as e:
        logger.error(f"HERMES chat error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando solicitud: {str(e)}",
        )


@router.post(
    "/mystic/analyze",
    response_model=MysticAnalyzeResponse,
    status_code=200,
    summary="Análisis profundo con MYSTIC",
    description="Envía datos a MYSTIC para análisis estratégico profundo",
)
async def mystic_analyze(
    body: MysticAnalyzeRequest,
    current_user: AuthUser,
):
    """
    MYSTIC: Estratega de sombra — analiza, detecta, advierte.

    - **data**: Texto para análisis
    - **analysis_type**: Tipo (fiscal | food | legal)
    - **conversation_id**: ID de conversación existente (opcional)

    Retorna:
    - **analysis**: Análisis profundo
    - **recommendations**: Lista de recomendaciones
    - **risk_level**: Nivel de riesgo (🔴 | 🟡 | 🟢)
    """
    try:
        async with get_tenant_session(current_user.tenant_id) as db:
            agent = MysticAgent(tenant_id=current_user.tenant_id, db=db)

            # Agregar contexto de tipo de análisis al mensaje
            message = f"[{body.analysis_type.upper()}]\n{body.data}"

            result = await agent.analyze(
                message=message,
                conversation_id=body.conversation_id,
                user_id=current_user.user_id,
            )

            # Extraer recomendaciones y nivel de riesgo del análisis
            # TODO: mejorar parsing para extraer estructura del response
            recommendations = []
            risk_level = "🟢"

            # Simple heuristic: si contiene 🔴 en la respuesta, marcar crítico
            if "🔴" in result["response"]:
                risk_level = "🔴"
            elif "🟡" in result["response"]:
                risk_level = "🟡"

            return MysticAnalyzeResponse(
                analysis=result["response"],
                recommendations=recommendations,
                risk_level=risk_level,
            )

    except Exception as e:
        logger.error(f"MYSTIC analyze error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando análisis: {str(e)}",
        )


@router.get(
    "/status",
    summary="Estado de los agentes",
    description="Retorna estado actual de HERMES y MYSTIC",
)
async def agents_status(current_user: AuthUser):
    """
    Obtiene el estado actual de los agentes disponibles para el tenant.

    Retorna:
    - **hermes**: Estado y modelo de HERMES
    - **mystic**: Estado y modelo de MYSTIC
    - **tenant_id**: ID del tenant autenticado
    """
    try:
        return {
            "hermes": {
                "status": "active",
                "model": "llama3:latest",
                "role": "orchestrator",
                "description": "Orquestador de luz",
            },
            "mystic": {
                "status": "active",
                "model": "mistral:latest",
                "role": "shadow_analyst",
                "description": "Estratega de sombra",
            },
            "tenant_id": str(current_user.tenant_id),
        }
    except Exception as e:
        logger.error(f"Status endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo estado de agentes",
        )
