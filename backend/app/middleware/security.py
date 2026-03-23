"""
middleware/security.py — Circuit Breaker para Ollama + Audit Logger de requests al Brain.
"""
import hashlib
import json
import logging
import time
from datetime import date, timedelta
from enum import Enum
from threading import Lock
from typing import Optional

logger = logging.getLogger(__name__)


# ── CIRCUIT BREAKER ───────────────────────────────────────────────────────────

class CircuitState(str, Enum):
    CLOSED = "CLOSED"        # Operación normal — Ollama responde bien
    OPEN = "OPEN"            # Ollama fallando — skip completo, usar solo RAG
    HALF_OPEN = "HALF_OPEN"  # Prueba de recuperación — un intento permitido


class OllamaCircuitBreaker:
    """
    Circuit Breaker para el servicio Ollama.

    - CLOSED   → Ollama responde. Si acumula `max_failures` fallos consecutivos → OPEN.
    - OPEN     → Ollama skipeado. Después de `reset_timeout` segundos → HALF_OPEN.
    - HALF_OPEN → Se permite un solo intento. Éxito → CLOSED. Fallo → vuelve a OPEN.

    Uso:
        cb = OllamaCircuitBreaker()

        if cb.allow_request():
            try:
                result = _ollama_ask(...)
                cb.record_success()
            except Exception:
                cb.record_failure()
                result = fallback_rag_answer
        else:
            result = fallback_rag_answer   # OPEN — no llamar Ollama
    """

    max_failures: int = 5
    reset_timeout: float = 60.0  # segundos antes de pasar a HALF_OPEN

    def __init__(self, max_failures: int = 5, reset_timeout: float = 60.0):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = Lock()

    # ── API pública ──────────────────────────────────────────────────────────

    def allow_request(self) -> bool:
        """Retorna True si se debe llamar a Ollama, False si el circuito está abierto."""
        with self._lock:
            if self._state == CircuitState.CLOSED:
                return True

            if self._state == CircuitState.OPEN:
                elapsed = time.monotonic() - (self._last_failure_time or 0)
                if elapsed >= self.reset_timeout:
                    logger.info("[CircuitBreaker] OPEN → HALF_OPEN (intentando recuperación)")
                    self._state = CircuitState.HALF_OPEN
                    return True
                return False

            # HALF_OPEN: ya se permitió el intento — no permitir más hasta que resuelva
            return True  # el primero en entrar en HALF_OPEN pasa

    def record_success(self) -> None:
        """Llamar tras una respuesta exitosa de Ollama."""
        with self._lock:
            if self._state != CircuitState.CLOSED:
                logger.info("[CircuitBreaker] %s → CLOSED (Ollama recuperado)", self._state)
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._last_failure_time = None

    def record_failure(self) -> None:
        """Llamar tras un error/timeout de Ollama."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()

            if self._state == CircuitState.HALF_OPEN:
                logger.warning("[CircuitBreaker] HALF_OPEN → OPEN (prueba fallida)")
                self._state = CircuitState.OPEN
                return

            if self._failure_count >= self.max_failures:
                logger.warning(
                    "[CircuitBreaker] CLOSED → OPEN (%d fallos consecutivos)",
                    self._failure_count,
                )
                self._state = CircuitState.OPEN

    @property
    def state(self) -> CircuitState:
        return self._state

    def status_dict(self) -> dict:
        """Información de estado legible para /api/metrics o /status."""
        return {
            "state": self._state.value,
            "failure_count": self._failure_count,
            "seconds_since_last_failure": (
                round(time.monotonic() - self._last_failure_time, 1)
                if self._last_failure_time
                else None
            ),
            "reset_timeout": self.reset_timeout,
        }


# Instancia global — importar desde aquí en main.py
ollama_circuit_breaker = OllamaCircuitBreaker(max_failures=5, reset_timeout=60.0)


# ── AUDIT LOGGER ─────────────────────────────────────────────────────────────

class AuditLogger:
    """
    Registra cada request a /api/brain/ask en Redis como lista por día.
    Retiene 7 días de logs. La pregunta se guarda hasheada (SHA-256) para privacidad.

    Formato de cada entrada (JSON):
        {
            "ts": "2026-03-23T14:05:30",
            "ip": "192.168.1.10",
            "question_hash": "abc123...",
            "source": "qdrant+ollama",
            "response_time_ms": 842,
            "tenant_id": "uuid-o-null",
            "channel": "whatsapp"
        }

    Clave Redis: audit:2026-03-23  (lista LPUSH, expire 7 días)
    """

    KEY_PREFIX = "audit"
    RETENTION_DAYS = 7

    def __init__(self, redis_client):
        """
        Args:
            redis_client: instancia de redis.Redis (ya conectada).
        """
        self._redis = redis_client

    def log(
        self,
        ip: str,
        question: str,
        source: str,
        response_time_ms: int,
        tenant_id: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> None:
        """
        Registra una entrada de auditoría. No lanza excepciones — falla silenciosa
        para no interrumpir el flujo del Brain.
        """
        try:
            question_hash = hashlib.sha256(question.encode()).hexdigest()[:16]
            today = date.today().isoformat()
            key = f"{self.KEY_PREFIX}:{today}"

            entry = json.dumps({
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
                "ip": ip,
                "question_hash": question_hash,
                "source": source,
                "response_time_ms": response_time_ms,
                "tenant_id": tenant_id,
                "channel": channel or "api",
            })

            pipe = self._redis.pipeline()
            pipe.lpush(key, entry)
            # TTL = segundos restantes del día + 7 días completos
            pipe.expire(key, self.RETENTION_DAYS * 86400)
            pipe.execute()

        except Exception as exc:
            logger.warning("[AuditLogger] No se pudo registrar entrada: %s", exc)

    def get_today(self) -> list[dict]:
        """Retorna los registros de hoy como lista de dicts (más reciente primero)."""
        try:
            key = f"{self.KEY_PREFIX}:{date.today().isoformat()}"
            raw = self._redis.lrange(key, 0, -1)
            return [json.loads(r) for r in raw]
        except Exception:
            return []

    def get_by_date(self, target_date: str) -> list[dict]:
        """
        Retorna registros de una fecha específica.

        Args:
            target_date: formato 'YYYY-MM-DD'
        """
        try:
            key = f"{self.KEY_PREFIX}:{target_date}"
            raw = self._redis.lrange(key, 0, -1)
            return [json.loads(r) for r in raw]
        except Exception:
            return []

    def summary_today(self) -> dict:
        """Resumen estadístico del día actual."""
        entries = self.get_today()
        if not entries:
            return {"date": date.today().isoformat(), "total": 0}

        by_source: dict[str, int] = {}
        latencies: list[int] = []

        for e in entries:
            src = e.get("source", "unknown")
            by_source[src] = by_source.get(src, 0) + 1
            ms = e.get("response_time_ms")
            if isinstance(ms, (int, float)):
                latencies.append(int(ms))

        avg_ms = round(sum(latencies) / len(latencies)) if latencies else 0

        return {
            "date": date.today().isoformat(),
            "total": len(entries),
            "by_source": by_source,
            "avg_response_time_ms": avg_ms,
            "p95_response_time_ms": (
                sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
            ),
        }
