"""
middleware/metrics.py — Contadores de latencia y uso por source/agente.
Almacena en Redis: incrementa contadores por source del Brain IA.

Claves Redis:
    metrics:{source}:count      → número de requests
    metrics:{source}:total_ms   → suma de ms (para calcular promedio)

Endpoint GET /api/metrics expuesto en main.py (sin auth, para monitoring).
"""
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

# Sources conocidos del Brain IA
KNOWN_SOURCES = [
    "tool:database_query",
    "tool:factura_pdf",
    "tool:nomina_calc",
    "qdrant+ollama",
    "rag+ollama",
    "qdrant_direct",
    "rag_direct",
    "qdrant_fallback",
    "rag_fallback",
    "swarm",
    "cache",
]


class AgentMetrics:
    """
    Registra métricas de latencia y conteo por source del Brain IA.

    Uso:
        metrics = AgentMetrics(redis_client)
        metrics.record(source="qdrant+ollama", response_time_ms=742)

    GET /api/metrics → metrics.get_all()
    """

    KEY_PREFIX = "metrics"

    def __init__(self, redis_client):
        self._redis = redis_client

    # ── Escritura ─────────────────────────────────────────────────────────────

    def record(self, source: str, response_time_ms: int) -> None:
        """
        Incrementa contador y suma de ms para el source dado.
        Falla silenciosa — no interrumpe el flujo del Brain.

        Args:
            source: identificador de origen (ej. 'qdrant+ollama', 'tool:database_query')
            response_time_ms: latencia de la respuesta en milisegundos
        """
        try:
            # Normalizar source: quitar caracteres no seguros para Redis
            safe_source = source.replace(" ", "_").replace("/", "_")[:64]
            count_key = f"{self.KEY_PREFIX}:{safe_source}:count"
            ms_key = f"{self.KEY_PREFIX}:{safe_source}:total_ms"

            pipe = self._redis.pipeline()
            pipe.incr(count_key)
            pipe.incrby(ms_key, max(0, response_time_ms))
            pipe.execute()

        except Exception as exc:
            logger.warning("[AgentMetrics] No se pudo registrar métrica: %s", exc)

    def record_error(self, source: str) -> None:
        """Registra un error para el source (latencia 0, cuenta el intento fallido)."""
        try:
            safe_source = source.replace(" ", "_").replace("/", "_")[:64]
            error_key = f"{self.KEY_PREFIX}:{safe_source}:errors"
            self._redis.incr(error_key)
        except Exception as exc:
            logger.warning("[AgentMetrics] No se pudo registrar error: %s", exc)

    # ── Lectura ───────────────────────────────────────────────────────────────

    def get_source(self, source: str) -> dict:
        """Retorna métricas de un source específico."""
        try:
            safe_source = source.replace(" ", "_").replace("/", "_")[:64]
            count_key = f"{self.KEY_PREFIX}:{safe_source}:count"
            ms_key = f"{self.KEY_PREFIX}:{safe_source}:total_ms"
            error_key = f"{self.KEY_PREFIX}:{safe_source}:errors"

            pipe = self._redis.pipeline()
            pipe.get(count_key)
            pipe.get(ms_key)
            pipe.get(error_key)
            count_raw, ms_raw, err_raw = pipe.execute()

            count = int(count_raw or 0)
            total_ms = int(ms_raw or 0)
            errors = int(err_raw or 0)
            avg_ms = round(total_ms / count) if count > 0 else 0

            return {
                "source": source,
                "count": count,
                "errors": errors,
                "total_ms": total_ms,
                "avg_ms": avg_ms,
            }
        except Exception:
            return {"source": source, "count": 0, "errors": 0, "total_ms": 0, "avg_ms": 0}

    def get_all(self) -> dict:
        """
        Retorna todos los contadores disponibles en Redis con prefijo 'metrics:'.
        Agrupa por source y calcula promedios.
        """
        try:
            # Descubrir todas las claves de conteo
            pattern = f"{self.KEY_PREFIX}:*:count"
            keys = self._redis.keys(pattern)

            sources_seen: set[str] = set()
            results: list[dict] = []

            for key in keys:
                key_str = key.decode() if isinstance(key, bytes) else key
                # Extraer source del formato: metrics:{source}:count
                parts = key_str.split(":")
                if len(parts) >= 3:
                    # source puede contener ":" (ej tool:database_query → metrics:tool:database_query:count)
                    source = ":".join(parts[1:-1])  # todo entre 'metrics:' y ':count'
                    if source not in sources_seen:
                        sources_seen.add(source)
                        results.append(self.get_source(source))

            # Ordenar por conteo descendente
            results.sort(key=lambda x: x["count"], reverse=True)

            total_requests = sum(r["count"] for r in results)
            total_errors = sum(r["errors"] for r in results)

            return {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "sources": results,
            }

        except Exception as exc:
            logger.warning("[AgentMetrics] Error al leer métricas: %s", exc)
            return {"total_requests": 0, "total_errors": 0, "sources": []}

    def reset_source(self, source: str) -> None:
        """Elimina todas las claves de un source (útil para tests)."""
        try:
            safe_source = source.replace(" ", "_").replace("/", "_")[:64]
            for suffix in ("count", "total_ms", "errors"):
                self._redis.delete(f"{self.KEY_PREFIX}:{safe_source}:{suffix}")
        except Exception:
            pass


# ── Context manager para medir latencia ──────────────────────────────────────

class measure:
    """
    Context manager conveniente para medir tiempo y registrar en AgentMetrics.

    Uso:
        with measure(metrics, "qdrant+ollama") as m:
            result = _ollama_ask(...)
        # m.elapsed_ms disponible después del bloque
    """

    def __init__(self, agent_metrics: AgentMetrics, source: str):
        self._metrics = agent_metrics
        self._source = source
        self._start: float = 0.0
        self.elapsed_ms: int = 0

    def __enter__(self):
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_ms = int((time.monotonic() - self._start) * 1000)
        if exc_type is not None:
            self._metrics.record_error(self._source)
        else:
            self._metrics.record(self._source, self.elapsed_ms)
        return False  # no suprimir la excepción
