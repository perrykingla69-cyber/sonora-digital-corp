"""
Endpoints de Agentes — HERMES y MYSTIC
RLS activo: cada request validado contra tenant_id
POST /hermes/chat — Orquestador con RAG + OpenRouter
GET /mystic/analyze — Análisis estratégico con alertas
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from uuid import UUID

from app.core.database import get_tenant_session
from app.schemas.agents import (
    HermesChatRequest,
    HermesChatResponse,
    MysticAnalyzeRequest,
    MysticAnalyzeResponse,
    AlertItem,
)
from app.services.agents import HermesService, MysticService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/hermes/chat",
    response_model=HermesChatResponse,
    status_code=200,
    summary="Chat con HERMES",
    description="Orquestador de luz — responde preguntas contables y empresariales con contexto RAG",
    responses={
        400: {"description": "Request inválido (tenant_id o message faltante)"},
        401: {"description": "No autorizado"},
        500: {"description": "Error en servidor (usa mock como fallback)"},
    },
)
async def hermes_chat(body: HermesChatRequest):
    """
    Chat con HERMES — Orquestador de Luz.

    Integración:
    - Valida tenant_id contra RLS (SET LOCAL)
    - Busca contexto RAG en Qdrant si use_rag=true
    - Llama OpenRouter API (Gemini Flash) con fallback a mock (timeout 5s)
    - Cache de respuestas en Redis (TTL 1h)

    Request:
    - **tenant_id**: UUID del tenant (requerido)
    - **message**: Pregunta (1-5000 chars, requerido)
    - **context**: Contexto adicional (opcional)
    - **use_rag**: Usar RAG search (default: true)

    Response:
    - **response**: Texto de respuesta
    - **sources**: Lista de fuentes (ej: qdrant_rag)
    - **confidence**: Score 0.0-1.0 (0.6 si mock, 0.95 si OpenRouter)
    - **processing_time_ms**: Tiempo de procesamiento
    - **used_mock**: true si OpenRouter no respondió en 5s
    """
    try:
        async with get_tenant_session(body.tenant_id) as db:
            response, sources, confidence, elapsed_ms, used_mock = await HermesService.chat(
                tenant_id=body.tenant_id,
                message=body.message,
                context=body.context,
                use_rag=body.use_rag,
                db=db,
            )

            return HermesChatResponse(
                response=response,
                sources=sources,
                confidence=confidence,
                processing_time_ms=elapsed_ms,
                used_mock=used_mock,
            )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"HERMES chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando solicitud (se intentó fallback a mock)",
        )


@router.get(
    "/mystic/analyze",
    response_model=MysticAnalyzeResponse,
    status_code=200,
    summary="Análisis profundo MYSTIC",
    description="Estratega de sombra — análisis fiscal, food o business con alertas",
    responses={
        400: {"description": "Parámetros inválidos"},
        401: {"description": "No autorizado"},
        404: {"description": "Tenant no encontrado"},
        500: {"description": "Error en servidor"},
    },
)
async def mystic_analyze(
    tenant_id: UUID = Query(..., description="UUID del tenant"),
    analysis_type: str = Query(..., pattern=r"^(fiscal|food|business)$", description="Tipo de análisis"),
):
    """
    Análisis Profundo — MYSTIC (Estratega de Sombra).

    Integración:
    - Escanea histórico de tenant (últimos 30 días)
    - Clasifica alertas por nivel (critical, warning, info)
    - Genera recomendaciones según type
    - Cache en Redis (TTL 1 hora)

    Query Params:
    - **tenant_id**: UUID del tenant (requerido)
    - **analysis_type**: fiscal | food | business (requerido)

    Response:
    - **analysis**: Texto de análisis
    - **alerts**: Lista de alertas con nivel y mensaje
    - **recommendations**: Recomendaciones accionables
    - **generated_at**: ISO 8601 timestamp
    - **used_mock**: true si no hay datos reales (MVP)
    """
    try:
        async with get_tenant_session(tenant_id) as db:
            analysis, alerts, recommendations, used_mock = await MysticService.analyze(
                tenant_id=tenant_id,
                analysis_type=analysis_type,
                db=db,
            )

            alert_items = [
                AlertItem(level=a["level"], message=a["message"], code=a.get("code"))
                for a in alerts
            ]

            return MysticAnalyzeResponse(
                analysis=analysis,
                alerts=alert_items,
                recommendations=recommendations,
                used_mock=used_mock,
            )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"MYSTIC analyze error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando análisis",
        )


@router.get(
    "/status",
    summary="Estado de agentes",
    description="Health check para HERMES y MYSTIC",
    responses={
        401: {"description": "No autorizado"},
    },
)
async def agents_status(tenant_id: UUID = Query(..., description="UUID del tenant")):
    """
    Estado de los agentes — HERMES y MYSTIC.

    Retorna información de disponibilidad y modelos.
    """
    try:
        async with get_tenant_session(tenant_id) as db:
            return {
                "hermes": {
                    "status": "active",
                    "model": "google/gemini-2.0-flash-001 (OpenRouter)",
                    "role": "orchestrator",
                    "description": "Orquestador de luz",
                },
                "mystic": {
                    "status": "active",
                    "model": "thudm/glm-z1-rumination (OpenRouter)",
                    "role": "shadow_analyst",
                    "description": "Estratega de sombra",
                },
                "rag": {
                    "status": "active",
                    "backend": "qdrant+ollama",
                    "embeddings": "nomic-embed-text (768-dim)",
                },
                "tenant_id": str(tenant_id),
            }
    except Exception as e:
        logger.error(f"Status check error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo estado de agentes",
        )
