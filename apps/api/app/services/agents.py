"""
Servicios para HERMES y MYSTIC — lógica centralizada de agentes.
Integración con OpenRouter API y RAG.
"""

import logging
import asyncio
import json
from typing import Optional, Tuple, List
from uuid import UUID
from datetime import datetime
import hashlib

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings
from app.core.redis import redis_client
from app.core.rag import search_context

logger = logging.getLogger(__name__)

HERMES_TIMEOUT = 30.0  # segundos (OpenRouter cold start puede tardar ~10s)
HERMES_MODEL = "google/gemini-2.0-flash-001"  # OpenRouter
MYSTIC_MODEL = "thudm/glm-z1-rumination:free"  # OpenRouter free tier
HERMES_CACHE_TTL = 3600  # 1 hora para respuestas frecuentes

MOCK_RESPONSES = {
    "hermes_default": "Soy HERMES, tu asistente de inteligencia empresarial. He analizado tu pregunta y aquí está mi respuesta basada en el contexto de tu empresa. ¿Hay algo más en lo que pueda ayudarte?",
    "mystic_fiscal": "Análisis fiscal: He detectado oportunidades en tu estructura contable. Se recomienda revisar deducciones por servicios profesionales (IVA acreditable) y aprovechar el régimen de pequeño contribuyente si aplica. Nivel de riesgo: 🟢 bajo.",
    "mystic_food": "Análisis de restaurante: Tu flujo de caja es saludable. Se detectó un incremento en costos de materia prima (+12% vs mes anterior). Recomendación: negociar con proveedores o ajustar márgenes. Nivel de riesgo: 🟡 moderado.",
    "mystic_business": "Análisis empresarial: Identifico un patrón de crecimiento consistente. Próximos pasos: diversificar ingresos y optimizar costos operativos. Nivel de riesgo: 🟢 bajo.",
}

MYSTIC_ALERTS = {
    "fiscal": [
        {"level": "info", "message": "Revisa deducciones de nómina", "code": "NOM-001"},
        {"level": "warning", "message": "Declaraciones próximas a vencer", "code": "DEC-001"},
    ],
    "food": [
        {"level": "info", "message": "Monitoreo de costos de materia prima activo", "code": "MAT-001"},
        {"level": "warning", "message": "Licencia sanitaria vence en 45 días", "code": "LIC-001"},
    ],
    "business": [
        {"level": "info", "message": "Análisis trimestral en progreso", "code": "TRIM-001"},
        {"level": "warning", "message": "Ratio de endeudamiento aumentó 3%", "code": "DEBT-001"},
    ],
}


class HermesService:
    """Servicio para HERMES — orquestador de luz."""

    @staticmethod
    def _cache_key(tenant_id: UUID, message: str) -> str:
        """Genera key de cache para respuesta."""
        h = hashlib.md5(
            f"{tenant_id}:{message.strip().lower()}".encode()
        ).hexdigest()
        return f"hermes:resp:{h}"

    @staticmethod
    async def _call_openrouter(
        messages: List[dict],
        timeout: float = HERMES_TIMEOUT,
    ) -> Optional[str]:
        """Llama OpenRouter API con fallback a timeout."""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                        "HTTP-Referer": "https://sonoradigitalcorp.com",
                    },
                    json={
                        "model": HERMES_MODEL,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 1024,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content")
        except asyncio.TimeoutError:
            logger.warning("OpenRouter timeout (5s) — usando mock")
            return None
        except httpx.HTTPError as e:
            logger.warning(f"OpenRouter HTTP error: {e} — usando mock")
            return None
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            return None

    @staticmethod
    async def chat(
        tenant_id: UUID,
        message: str,
        context: Optional[str] = None,
        use_rag: bool = True,
        db: Optional[AsyncSession] = None,
    ) -> Tuple[str, List[str], float, int, bool]:
        """
        Chat con HERMES.

        Returns: (response, sources, confidence, processing_time_ms, used_mock)
        """
        import time
        start = time.time()

        # Combinar mensaje con contexto
        full_message = message
        if context:
            full_message = f"{context}\n\n{message}"

        # Buscar en cache
        cache_key = HermesService._cache_key(tenant_id, message)
        cached = await redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            return (data["response"], data["sources"], 0.95, int((time.time() - start) * 1000), False)

        # RAG: búsqueda en Qdrant
        sources = []
        rag_context = ""
        if use_rag and db:
            try:
                rag_context = await search_context(message, tenant_id)
                if rag_context:
                    sources = ["qdrant_rag"]
            except Exception as e:
                logger.warning(f"RAG search failed: {e}")

        # Construir prompt
        system = """Eres HERMES, el orquestador de inteligencia empresarial de Sonora Digital Corp.
- Responde preguntas contables, fiscales y empresariales en español mexicano
- Eres claro, directo y profesional
- Si no sabes algo, lo dices
- NUNCA inventas datos financieros o regulatorios
- Si necesitas análisis profundo, coordina con MYSTIC"""

        if rag_context:
            system += f"\n\nCONTEXTO:\n{rag_context}"

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": full_message},
        ]

        # Llamar OpenRouter (con fallback a mock si timeout)
        response = await HermesService._call_openrouter(messages)
        used_mock = False

        if not response:
            response = MOCK_RESPONSES["hermes_default"]
            used_mock = True
            confidence = 0.6
        else:
            confidence = 0.95

        # Guardar en cache
        cache_data = {
            "response": response,
            "sources": sources,
        }
        try:
            await redis_client.setex(
                cache_key,
                HERMES_CACHE_TTL,
                json.dumps(cache_data)
            )
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")

        elapsed_ms = int((time.time() - start) * 1000)
        return (response, sources, confidence, elapsed_ms, used_mock)


class MysticService:
    """Servicio para MYSTIC — estratega de sombra."""

    @staticmethod
    def _cache_key(tenant_id: UUID, analysis_type: str) -> str:
        """Genera key de cache para análisis."""
        return f"mystic:analyze:{tenant_id}:{analysis_type}"

    @staticmethod
    async def analyze(
        tenant_id: UUID,
        analysis_type: str,
        data: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> Tuple[str, List[dict], List[str], bool]:
        """
        Análisis profundo MYSTIC.

        Returns: (analysis, alerts, recommendations, used_mock)
        """
        # Validar tipo
        if analysis_type not in ("fiscal", "food", "business"):
            analysis_type = "business"

        # Buscar en cache (TTL 1 hora)
        cache_key = MysticService._cache_key(tenant_id, analysis_type)
        cached = await redis_client.get(cache_key)
        if cached:
            data_obj = json.loads(cached)
            return (
                data_obj["analysis"],
                data_obj["alerts"],
                data_obj["recommendations"],
                False
            )

        # Obtener contexto del tenant si es posible
        tenant_context = ""
        if db:
            try:
                result = await db.execute(
                    text("SELECT name, plan FROM tenants WHERE id = :tid"),
                    {"tid": str(tenant_id)}
                )
                tenant = result.fetchone()
                if tenant:
                    tenant_context = f"\nEmpresa: {tenant[0]} | Plan: {tenant[1]}"
            except Exception as e:
                logger.warning(f"Tenant context fetch failed: {e}")

        # Construir análisis
        system = f"""Eres MYSTIC, el analista estratégico de Sonora Digital Corp.
- Detectas patrones, riesgos y oportunidades
- Especializado en análisis {analysis_type}
- Formato: OBSERVACIÓN | ANÁLISIS | RIESGO/OPORTUNIDAD | RECOMENDACIÓN
- Siempre fundamentado en datos{tenant_context}"""

        prompt = data or f"Realiza un análisis profundo de situación {analysis_type} del tenant."

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]

        # Llamar OpenRouter con modelo de razonamiento MYSTIC
        ai_response = None
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                        "HTTP-Referer": "https://sonoradigitalcorp.com",
                    },
                    json={
                        "model": MYSTIC_MODEL,
                        "messages": messages,
                        "temperature": 0.4,
                        "max_tokens": 2048,
                    },
                )
                r.raise_for_status()
                ai_response = r.json().get("choices", [{}])[0].get("message", {}).get("content")
        except Exception as e:
            logger.warning(f"MYSTIC OpenRouter error: {e} — usando mock")

        used_mock = ai_response is None
        analysis = ai_response or MOCK_RESPONSES.get(f"mystic_{analysis_type}", MOCK_RESPONSES["mystic_business"])
        alerts = MYSTIC_ALERTS.get(analysis_type, [])
        recommendations = (
            ["Análisis generado por MYSTIC con IA — revisar hallazgos"]
            if not used_mock else
            ["Revisar reporte mensual", "Coordinar con equipo de operaciones", "Documentar hallazgos"]
        )

        # Guardar en cache
        cache_data = {
            "analysis": analysis,
            "alerts": alerts,
            "recommendations": recommendations,
        }
        try:
            await redis_client.setex(
                cache_key,
                3600,
                json.dumps(cache_data)
            )
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")

        return (analysis, alerts, recommendations, used_mock)
