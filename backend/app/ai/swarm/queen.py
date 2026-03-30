"""Hermes Brain — Queen-Worker Swarm."""
from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)

_COL_FISCAL = "fiscal"
_COL_CONTADOR = "contador"
_COL_ADUANAS = "aduanas"
_COL_RRHH = "rrhh"
_COL_ADMIN = "admin"
_COL_VENTAS = "ventas"
_COL_LOGISTICA = "logistica"
_COL_USA_TRADE = "usa_trade"

_CACHE_PREFIX = "queen:answer:"
_CACHE_TTL_SECONDS = 3600
_MAX_INPUT_LEN = 1000
_MAX_MEMORY_CHARS = 300
_MAX_CHUNKS_PER_WORKER = 4

_FALLBACK_GLM = "glm"
_FALLBACK_CLAUDE = "claude"
_FALLBACK_RAG_FIRSTLINE = "rag_firstline"

_KW_FISCAL = {
    "factura",
    "cfdi",
    "ingreso",
    "egreso",
    "isr",
    "sat",
    "deduccion",
    "deducible",
    "declaracion",
    "fiscal",
    "contabilidad",
}
_KW_NOMINA = {
    "nomina",
    "nómina",
    "sueldo",
    "salario",
    "empleado",
    "imss",
    "infonavit",
    "retencion",
    "retención",
}
_KW_IVA = {
    "iva",
    "diot",
    "acreditar",
    "acreditamiento",
    "tasa",
    "exento",
    "impuesto",
}
_KW_ADUANAS = {
    "pedimento",
    "arancel",
    "fracción",
    "aduana",
    "importación",
    "exportación",
    "mve",
    "incoterm",
    "operador",
    "agente aduanal",
    "comercio exterior",
    "regla octava",
}
_KW_ADMIN = {
    "administración",
    "operaciones",
    "recursos",
    "contrato",
    "política",
    "proceso",
    "manual",
    "reglamento",
    "gestión",
}


@dataclass
class AgentResult:
    agent: str
    answer: str
    confidence: float
    sources: list[str] = field(default_factory=list)
    chunks_used: int = 0
    fallback_used: str | None = None


class WorkerAgent:
    """Agente especialista para recuperar contexto y responder."""

    def __init__(
        self,
        name: str,
        specialty: str,
        collections: list[str],
        keywords: set[str],
    ) -> None:
        self.name = name
        self.specialty = specialty
        self.collections = collections
        self.keywords = keywords

    def is_relevant(self, question: str) -> bool:
        q = question.lower()
        return any(re.search(r"\b" + re.escape(keyword) + r"\b", q) for keyword in self.keywords)

    async def _invoke_model(
        self,
        model_fn: Callable,
        question: str,
        context: str,
        loop: asyncio.AbstractEventLoop,
    ) -> str:
        if inspect.iscoroutinefunction(model_fn):
            return await model_fn(question, context)
        result = model_fn(question, context)
        if inspect.isawaitable(result):
            return await result
        return await loop.run_in_executor(None, lambda: result)

    async def run(
        self,
        question: str,
        rag_fn: Callable,
        ollama_fn: Callable,
        loop: asyncio.AbstractEventLoop,
        glm_fn: Callable | None = None,
        claude_fn: Callable | None = None,
    ) -> AgentResult:
        all_chunks: list[dict[str, Any]] = []
        for collection in self.collections:
            chunks = await rag_fn(question, collection, limit=2)
            if isinstance(chunks, list):
                all_chunks.extend(chunks)

        dedup: dict[str, dict[str, Any]] = {}
        for chunk in all_chunks:
            key = (chunk.get("doc_id") or chunk.get("text", "")[:60]).strip()
            if key and key not in dedup:
                dedup[key] = chunk

        chunks = sorted(
            dedup.values(),
            key=lambda item: float(item.get("score", 0.0) or 0.0),
            reverse=True,
        )[:_MAX_CHUNKS_PER_WORKER]

        if not chunks:
            return AgentResult(agent=self.name, answer="", confidence=0.0)

        parts = [f"[{c.get('doc_id', '')}]\n{c.get('text', '')[:_MAX_MEMORY_CHARS]}" for c in chunks]
        rag_context = "\n\n".join(parts)
        specialized_question = f"[{self.specialty}] {question}"

        fallback_used: str | None = None
        answer = ""

        try:
            answer = await self._invoke_model(ollama_fn, specialized_question, rag_context, loop)
        except Exception as error:
            logger.warning("%s ollama error: %s", self.name, error)
            if glm_fn:
                try:
                    answer = await self._invoke_model(glm_fn, specialized_question, rag_context, loop)
                    fallback_used = _FALLBACK_GLM
                except Exception as glm_error:
                    logger.warning("%s glm error: %s", self.name, glm_error)
            if not answer and claude_fn:
                try:
                    answer = await self._invoke_model(claude_fn, specialized_question, rag_context, loop)
                    fallback_used = _FALLBACK_CLAUDE
                except Exception as claude_error:
                    logger.warning("%s claude error: %s", self.name, claude_error)
            if not answer:
                answer = (chunks[0].get("text", "").split("\n")[0].strip())[:200]
                fallback_used = _FALLBACK_RAG_FIRSTLINE

        scores = [float(chunk.get("score", 0.0) or 0.0) for chunk in chunks]
        confidence = min(1.0, (sum(scores) / len(scores)) if scores else 0.0)
        sources = [str(chunk.get("doc_id", "")) for chunk in chunks]

        return AgentResult(
            agent=self.name,
            answer=answer,
            confidence=confidence,
            sources=sources,
            chunks_used=len(chunks),
            fallback_used=fallback_used,
        )


class QueenAgent:
    """Orquestadora principal del swarm."""

    def __init__(self) -> None:
        self.workers: list[WorkerAgent] = [
            WorkerAgent(
                name="AgentFiscal",
                specialty="Especialista fiscal y contable",
                collections=[_COL_FISCAL, _COL_CONTADOR, _COL_VENTAS],
                keywords=_KW_FISCAL,
            ),
            WorkerAgent(
                name="AgentNomina",
                specialty="Especialista en nómina",
                collections=[_COL_FISCAL, _COL_RRHH],
                keywords=_KW_NOMINA,
            ),
            WorkerAgent(
                name="AgentIVA",
                specialty="Especialista en IVA",
                collections=[_COL_FISCAL, _COL_CONTADOR],
                keywords=_KW_IVA,
            ),
            WorkerAgent(
                name="AgentAduanas",
                specialty="Especialista en aduanas y comercio exterior",
                collections=[_COL_ADUANAS, _COL_USA_TRADE],
                keywords=_KW_ADUANAS,
            ),
            WorkerAgent(
                name="AgentAdmin",
                specialty="Especialista en administración y operaciones",
                collections=[_COL_ADMIN, _COL_VENTAS],
                keywords=_KW_ADMIN,
            ),
        ]

    def _sanitize(self, text: str) -> str:
        sanitized = text.strip()[:_MAX_INPUT_LEN]
        sanitized = re.sub(r"[\x00-\x1f\x7f]", "", sanitized)
        return sanitized

    def _route(self, question: str) -> list[WorkerAgent]:
        relevant = [worker for worker in self.workers if worker.is_relevant(question)]
        return relevant if relevant else self.workers

    def _consolidate(self, results: list[AgentResult]) -> tuple[str, str | None]:
        valid = [result for result in results if result.answer and result.confidence > 0]
        if not valid:
            return "No encontré información suficiente para responder esta consulta.", None

        valid.sort(key=lambda result: result.confidence, reverse=True)
        primary = valid[0]
        supplements: list[str] = []

        for result in valid[1:]:
            if result.confidence <= 0.4:
                continue
            first = result.answer.split(".")[0].strip()
            if len(first) > 20:
                supplements.append(f"[{result.agent}] {first}.")
            if len(supplements) >= 2:
                break

        if supplements:
            return primary.answer + "\n\n" + "\n".join(supplements), primary.fallback_used
        return primary.answer, primary.fallback_used

    def _cache_key(self, question: str) -> str:
        digest = hashlib.md5(question.lower().strip().encode("utf-8")).hexdigest()
        return f"{_CACHE_PREFIX}{digest}"

    async def run(
        self,
        question: str,
        rag_fn: Callable,
        ollama_fn: Callable,
        redis_get: Callable[[str], str | None] | None = None,
        redis_set: Callable[[str, str, int], None] | None = None,
        glm_fn: Callable | None = None,
        claude_fn: Callable | None = None,
    ) -> dict[str, Any]:
        sanitized_question = self._sanitize(question)
        was_sanitized = sanitized_question != question
        cache_key = self._cache_key(sanitized_question)

        if redis_get:
            try:
                cached = redis_get(cache_key)
                if cached:
                    payload = json.loads(cached)
                    payload["cache_hit"] = True
                    payload["sanitized"] = was_sanitized
                    return payload
            except Exception as error:
                logger.warning("Queen redis_get error: %s", error)

        workers = self._route(sanitized_question)
        workers_routed = [worker.name for worker in workers]
        loop = asyncio.get_running_loop()

        logger.info("Queen routing '%s' -> %s", sanitized_question[:80], workers_routed)

        tasks = [
            worker.run(
                sanitized_question,
                rag_fn,
                ollama_fn,
                loop,
                glm_fn=glm_fn,
                claude_fn=claude_fn,
            )
            for worker in workers
        ]

        raw_results = await asyncio.gather(*tasks, return_exceptions=True)
        results: list[AgentResult] = []
        for result in raw_results:
            if isinstance(result, AgentResult):
                results.append(result)
            elif isinstance(result, Exception):
                logger.warning("Queen worker error: %s", result)

        answer, fallback_used = self._consolidate(results)

        response: dict[str, Any] = {
            "answer": answer,
            "agents_used": [result.agent for result in results if result.answer],
            "confidences": {result.agent: round(result.confidence, 4) for result in results},
            "total_chunks": sum(result.chunks_used for result in results),
            "cache_hit": False,
            "fallback_used": fallback_used,
            "workers_routed": workers_routed,
            "sanitized": was_sanitized,
        }

        if redis_set:
            try:
                redis_set(cache_key, json.dumps(response, ensure_ascii=False), _CACHE_TTL_SECONDS)
            except Exception as error:
                logger.warning("Queen redis_set error: %s", error)

        return response


queen = QueenAgent()
