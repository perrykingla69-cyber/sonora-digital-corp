"""
HERMES BRAIN — Sistema de capas auto-mejorante
Sonora Digital Corp

Arquitectura:
  Capa 1: Cálculos Python deterministas (0ms, $0, exacto)
  Capa 2: Redis caché de respuestas (1ms, $0)
  Capa 3: Qdrant RAG semántico (50ms, $0)
  Capa 4: LLM OpenRouter (3s, ~$0.001) → APRENDE → guarda en capas 1-3

Con cada uso: el sistema se vuelve más rápido y más barato.
"""

import asyncio
import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import httpx
import redis.asyncio as aioredis
from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.fiscal.calculos import (
    detectar_calculo, calcular_isr_mensual, calcular_iva,
    calcular_cuotas_imss, validar_cfdi_totales,
    calcular_contribuciones_importacion, calcular_manifestacion_valor,
    dias_para_declaracion,
)

logger = logging.getLogger("hermes.brain")

REDIS_URL    = os.environ.get("REDIS_URL", "redis://redis:6379/0")
QDRANT_URL   = os.environ.get("QDRANT_URL", "http://qdrant:6333")
OLLAMA_URL   = os.environ.get("OLLAMA_URL", "http://ollama:11434")
OPENROUTER   = os.environ.get("OPENROUTER_API_KEY", "")
LLM_MODEL    = os.environ.get("HERMES_MODEL", "google/gemini-2.0-flash-001")
EMBED_MODEL  = "nomic-embed-text"
CACHE_TTL    = 86400   # 24h en Redis
MIN_SCORE    = 0.78    # umbral de confianza Qdrant


@dataclass
class RespuestaCerebro:
    texto: str
    fuente: str          # "calculo_python" | "redis_cache" | "qdrant_rag" | "llm"
    confianza: float
    costo_tokens: int = 0
    fundamento: Optional[str] = None
    tiempo_ms: int = 0


class HermesBrain:
    """
    El cerebro de HERMES. Se llama una vez por query del cliente.
    Nunca va al LLM si hay algo en capas superiores.
    """

    def __init__(self):
        self.redis   = aioredis.from_url(REDIS_URL, decode_responses=True)
        self.qdrant  = AsyncQdrantClient(url=QDRANT_URL)
        self.llm     = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER,
        )

    # ── API pública ───────────────────────────────────────────
    async def query(
        self,
        pregunta: str,
        tenant_id: str,
        niche: str = "general",
        contexto_extra: str = "",
    ) -> RespuestaCerebro:
        start = asyncio.get_event_loop().time()

        # CAPA 1: cálculo determinista
        resp = await self._capa_calculos(pregunta)
        if resp:
            resp.tiempo_ms = int((asyncio.get_event_loop().time() - start) * 1000)
            await self._incrementar_stat("calculo_python")
            return resp

        # CAPA 2: Redis caché
        resp = await self._capa_redis(pregunta, tenant_id)
        if resp:
            resp.tiempo_ms = int((asyncio.get_event_loop().time() - start) * 1000)
            await self._incrementar_stat("redis_cache")
            return resp

        # CAPA 3: Qdrant RAG
        resp = await self._capa_qdrant(pregunta, tenant_id, niche)
        if resp:
            resp.tiempo_ms = int((asyncio.get_event_loop().time() - start) * 1000)
            # Guardar en Redis para próxima vez
            await self._guardar_redis(pregunta, tenant_id, resp)
            await self._incrementar_stat("qdrant_rag")
            return resp

        # CAPA 4: LLM (último recurso)
        resp = await self._capa_llm(pregunta, tenant_id, niche, contexto_extra)
        resp.tiempo_ms = int((asyncio.get_event_loop().time() - start) * 1000)
        # APRENDER: guardar en Redis + Qdrant para no pagar esta pregunta de nuevo
        await self._aprender(pregunta, tenant_id, niche, resp)
        await self._incrementar_stat("llm_inference")
        return resp

    # ── CAPA 1: Python determinista ───────────────────────────
    async def _capa_calculos(self, pregunta: str) -> Optional[RespuestaCerebro]:
        tipo = detectar_calculo(pregunta)
        if not tipo:
            return None

        try:
            # Extraer número de la pregunta si existe
            import re
            numeros = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', pregunta.replace(',', ''))
            num = float(numeros[0]) if numeros else None

            resultado = None
            if tipo == "isr_mensual" and num:
                r = calcular_isr_mensual(num)
                resultado = f"ISR mensual sobre ${num:,.2f}: **${r.valor:,.2f}**\n\n{r.formula}\n\n📋 Fundamento: {r.fundamento}"

            elif tipo == "iva" and num:
                r = calcular_iva(num)
                resultado = f"IVA (16%) sobre ${num:,.2f}: **${r.valor:,.2f}**\n\n{r.formula}\n\n📋 {r.fundamento}"

            elif tipo == "declaracion":
                for oblig in ["pago_provisional_pm", "diot_mensual", "declaracion_anual_pf"]:
                    d = dias_para_declaracion(oblig)
                    if "dias_restantes" in d:
                        urgencia = "⚠️ URGENTE" if d["urgente"] else "✅"
                        resultado = (resultado or "") + f"\n{urgencia} **{d['obligacion']}**: {d['dias_restantes']} días ({d['vencimiento']})"

            if resultado:
                return RespuestaCerebro(
                    texto=resultado,
                    fuente="calculo_python",
                    confianza=1.0,
                    fundamento="Función fiscal determinista — Art. LISR/LIVA/LSS 2025",
                )
        except Exception as e:
            logger.debug(f"Capa cálculos: {e}")

        return None

    # ── CAPA 2: Redis caché ───────────────────────────────────
    def _cache_key(self, pregunta: str, tenant_id: str) -> str:
        h = hashlib.sha256(f"{tenant_id}:{pregunta.lower().strip()}".encode()).hexdigest()[:16]
        return f"brain:cache:{h}"

    async def _capa_redis(self, pregunta: str, tenant_id: str) -> Optional[RespuestaCerebro]:
        try:
            key = self._cache_key(pregunta, tenant_id)
            data = await self.redis.get(key)
            if data:
                d = json.loads(data)
                return RespuestaCerebro(**d)
        except Exception as e:
            logger.debug(f"Redis cache miss: {e}")
        return None

    async def _guardar_redis(self, pregunta: str, tenant_id: str, resp: RespuestaCerebro):
        try:
            key = self._cache_key(pregunta, tenant_id)
            await self.redis.setex(key, CACHE_TTL, json.dumps({
                "texto": resp.texto,
                "fuente": f"redis_cache(via:{resp.fuente})",
                "confianza": resp.confianza,
                "fundamento": resp.fundamento,
                "tiempo_ms": 0,
            }))
        except Exception as e:
            logger.debug(f"Redis save error: {e}")

    # ── CAPA 3: Qdrant RAG ────────────────────────────────────
    async def _embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": EMBED_MODEL, "prompt": text},
            )
            return r.json()["embedding"]

    async def _capa_qdrant(self, pregunta: str, tenant_id: str, niche: str) -> Optional[RespuestaCerebro]:
        try:
            vector = await self._embed(pregunta)
            colecciones = [f"global_{niche}", "global_fiscal_mx", f"tenant_{tenant_id}"]

            mejor_score = 0
            mejor_texto = None
            mejor_fuente = None

            for col in colecciones:
                try:
                    results = await self.qdrant.search(
                        collection_name=col,
                        query_vector=vector,
                        limit=3,
                        score_threshold=MIN_SCORE,
                    )
                    for r in results:
                        if r.score > mejor_score:
                            mejor_score = r.score
                            mejor_texto = r.payload.get("text", "")
                            mejor_fuente = r.payload.get("source", col)
                except Exception:
                    continue

            if mejor_texto and mejor_score >= MIN_SCORE:
                return RespuestaCerebro(
                    texto=mejor_texto,
                    fuente="qdrant_rag",
                    confianza=mejor_score,
                    fundamento=f"Fuente: {mejor_fuente} (relevancia: {mejor_score:.0%})",
                )
        except Exception as e:
            logger.debug(f"Qdrant error: {e}")
        return None

    # ── CAPA 4: LLM ──────────────────────────────────────────
    async def _capa_llm(self, pregunta: str, tenant_id: str,
                         niche: str, contexto: str) -> RespuestaCerebro:
        system = f"""Eres HERMES, asistente fiscal y de negocios para PYMEs mexicanas.
Giro del cliente: {niche}.
Reglas:
- NUNCA inventes artículos, montos, fechas o leyes
- Si no sabes algo con certeza, dilo claramente
- Cita siempre el fundamento legal (Art. X de Ley Y)
- Responde en español mexicano, tono ejecutivo y cálido
- Sé conciso: máx 3 párrafos salvo que pidan detalle"""

        messages = [{"role": "system", "content": system}]
        if contexto:
            messages.append({"role": "user", "content": f"Contexto relevante:\n{contexto}"})
        messages.append({"role": "user", "content": pregunta})

        r = await self.llm.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            max_tokens=800,
        )
        texto = r.choices[0].message.content
        tokens = r.usage.total_tokens if r.usage else 0

        return RespuestaCerebro(
            texto=texto,
            fuente="llm",
            confianza=0.85,
            costo_tokens=tokens,
            fundamento="Generado por LLM — verificar con contador",
        )

    # ── APRENDER: LLM → Qdrant ────────────────────────────────
    async def _aprender(self, pregunta: str, tenant_id: str,
                         niche: str, resp: RespuestaCerebro):
        """
        Guarda la respuesta del LLM en Qdrant y Redis.
        La próxima vez que alguien haga pregunta similar → no se paga LLM.
        """
        try:
            # Guardar en Redis
            await self._guardar_redis(pregunta, tenant_id, resp)

            # Guardar en Qdrant colección del tenant
            from qdrant_client.models import PointStruct, VectorParams, Distance
            import uuid

            col = f"tenant_{tenant_id}"
            vector = await self._embed(f"{pregunta}\n{resp.texto}")

            punto = PointStruct(
                id=int(hashlib.md5(f"{tenant_id}:{pregunta}".encode()).hexdigest(), 16) % (2**63),
                vector={"default": vector},
                payload={
                    "text": resp.texto,
                    "pregunta_original": pregunta,
                    "source": "llm_aprendido",
                    "niche": niche,
                    "tenant_id": tenant_id,
                    "aprendido_en": datetime.utcnow().isoformat(),
                    "fundamento": resp.fundamento,
                    "validado": False,  # Human in the loop: contador puede validar
                },
            )

            try:
                await self.qdrant.upsert(collection_name=col, points=[punto])
                logger.info(f"✅ Aprendido y guardado en {col}")
            except Exception:
                # Si la colección no existe, crearla
                await self.qdrant.create_collection(
                    col, vectors_config=VectorParams(size=768, distance=Distance.COSINE)
                )
                await self.qdrant.upsert(collection_name=col, points=[punto])

        except Exception as e:
            logger.error(f"Error al aprender: {e}")

    # ── Estadísticas de uso ───────────────────────────────────
    async def _incrementar_stat(self, capa: str):
        try:
            hoy = datetime.utcnow().strftime("%Y-%m-%d")
            await self.redis.hincrby(f"brain:stats:{hoy}", capa, 1)
        except Exception:
            pass

    async def get_stats(self) -> dict:
        """Muestra eficiencia del brain: % de preguntas por capa."""
        try:
            hoy = datetime.utcnow().strftime("%Y-%m-%d")
            stats = await self.redis.hgetall(f"brain:stats:{hoy}")
            total = sum(int(v) for v in stats.values()) or 1
            return {
                "fecha": hoy,
                "total_queries": total,
                "por_capa": {k: {"count": int(v), "pct": f"{int(v)/total*100:.1f}%"}
                             for k, v in stats.items()},
                "costo_evitado": f"~${(int(stats.get('qdrant_rag', 0)) + int(stats.get('redis_cache', 0)) + int(stats.get('calculo_python', 0))) * 0.001:.3f} USD hoy",
            }
        except Exception:
            return {}


# Instancia global (singleton)
_brain: Optional[HermesBrain] = None

def get_brain() -> HermesBrain:
    global _brain
    if _brain is None:
        _brain = HermesBrain()
    return _brain
