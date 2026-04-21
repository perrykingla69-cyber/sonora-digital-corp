"""
Endpoints de Fiscal Agent — Operaciones contables determinísticas
RLS activo: cada request validado contra tenant_id
POST /fiscal/{operation} — Ejecuta operación determinística en fiscal-agent
GET /fiscal/health — Health check de fiscal-agent
"""

import logging
import httpx
import asyncio
from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from typing import Any

from app.core.database import get_tenant_session
from app.schemas.agents import FiscalOperationRequest, FiscalOperationResponse

logger = logging.getLogger(__name__)
router = APIRouter()

FISCAL_AGENT_URL = "http://fiscal-agent:8001"
FISCAL_AGENT_TIMEOUT = 2.0  # segundos


async def call_fiscal_agent(operation: str, inputs: dict, tenant_id: UUID) -> dict:
    """
    Llama fiscal-agent microapp vía HTTP POST.
    Returns: {success: bool, data: dict|null, error: str|null, latency_ms: int}
    """
    try:
        async with httpx.AsyncClient(timeout=FISCAL_AGENT_TIMEOUT) as client:
            response = await client.post(
                f"{FISCAL_AGENT_URL}/operate",
                json={
                    "operation": operation,
                    "inputs": inputs,
                    "tenant_id": str(tenant_id),
                },
            )
            response.raise_for_status()
            return response.json()
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "Fiscal Agent timeout (>2s)",
            "data": None,
            "latency_ms": int(FISCAL_AGENT_TIMEOUT * 1000),
        }
    except httpx.RequestError as e:
        logger.error(f"Fiscal Agent connection error: {e}")
        return {
            "success": False,
            "error": "Fiscal Agent unavailable",
            "data": None,
            "latency_ms": 0,
        }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"Fiscal Agent error: {e.response.text}",
            "data": None,
            "latency_ms": 0,
        }


@router.post(
    "/fiscal/{operation}",
    response_model=FiscalOperationResponse,
    status_code=200,
    summary="Ejecutar operación fiscal",
    description="Operación determinística: validate_cfdi, calculate_taxes, check_compliance, etc.",
    responses={
        400: {"description": "Request inválido o operación no existe"},
        401: {"description": "No autorizado"},
        500: {"description": "Error en Fiscal Agent"},
    },
)
async def execute_fiscal_operation(
    operation: str,
    body: FiscalOperationRequest,
):
    """
    Ejecuta operación fiscal determinística en Fiscal Agent.

    Operaciones disponibles:
    - **validate_cfdi**: Valida estructura CFDI 4.0
    - **calculate_taxes**: Calcula ISR/IVA basado en ingresos/gastos/régimen
    - **check_compliance**: Obtiene obligaciones y deadlines
    - **get_tax_catalogs**: Lookup de tablas SAT
    - **validate_receipt**: Valida deducibilidad de recibo
    - **alert_deadline**: Fecha exacta + alertas
    - **suggest_deductions**: Sugerencias deducibles por régimen
    - **generate_compliance_report**: Resumen ejecutivo obligaciones

    Request:
    - **tenant_id**: UUID del tenant (requerido)
    - **inputs**: Dict con parámetros de operación

    Response:
    - **success**: bool
    - **data**: Resultado de operación (dict)
    - **error**: Mensaje de error si no exitosa
    - **latency_ms**: Tiempo procesamiento en ms
    """
    try:
        # Valida tenant_id contra RLS (context manager)
        async with get_tenant_session(body.tenant_id) as db:
            # Llamada a fiscal-agent
            result = await call_fiscal_agent(operation, body.inputs, body.tenant_id)

            if not result["success"]:
                logger.warning(f"Fiscal operation '{operation}' failed: {result['error']}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["error"],
                )

            return FiscalOperationResponse(
                success=result["success"],
                data=result["data"],
                error=result["error"],
                latency_ms=result["latency_ms"],
            )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Fiscal operation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error ejecutando operación fiscal",
        )


@router.get(
    "/fiscal/health",
    status_code=200,
    summary="Health check Fiscal Agent",
    description="Valida disponibilidad de Fiscal Agent",
)
async def fiscal_agent_health():
    """
    Health check — Fiscal Agent.

    Retorna estado de Fiscal Agent y operaciones disponibles.
    """
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{FISCAL_AGENT_URL}/health")
            response.raise_for_status()
            health_data = response.json()

            return {
                "status": "ok",
                "fiscal_agent": health_data,
                "integration": "healthy",
            }
    except Exception as e:
        logger.error(f"Fiscal Agent health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fiscal Agent unavailable",
        )
