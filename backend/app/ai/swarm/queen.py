"""
Mystic Brain — Queen-Worker Swarm
Queen coordina 3 agentes especializados en paralelo para preguntas complejas.

Arquitectura:
  Usuario → Queen → [AgentFacturas | AgentNomina | AgentIVA] → Consenso → Respuesta
"""
from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)


# ── Keywords por especialidad ─────────────────────────────────────────────────

_KW_FACTURAS = {
    "factura", "cfdi", "ingreso", "egreso", "gasto", "compra", "venta",
    "subtotal", "timbrar", "uuid", "emisor", "receptor", "folio", "xml",
    "nota", "crédito", "complemento", "concepto", "contabilidad",
    "deducible", "proveedor", "cliente",
}
_KW_NOMINA = {
    "nómina", "nomina", "sueldo", "salario", "trabajador", "empleado",
    "imss", "infonavit", "isr", "retención", "retencion", "subsidio",
    "cuotas", "percepciones", "deducciones", "nss", "consar", "finiquito",
    "liquidación", "liquidacion",
}
_KW_IVA = {
    "iva", "acreditar", "acreditamiento", "diot", "tasa", "exento",
    "trasladado", "retenido", "saldo", "favor", "cargo", "prorrateo",
    "gravadas", "importación", "importacion", "impuesto", "declaración",
    "declaracion", "sat",
}


# ── Resultado de agente ───────────────────────────────────────────────────────

@dataclass
class AgentResult:
    agent: str
    answer: str
    confidence: float          # 0.0–1.0
    sources: list[str] = field(default_factory=list)
    chunks_used: int = 0


# ── Worker especializado ──────────────────────────────────────────────────────

class WorkerAgent:
    """Agente que busca en Qdrant y genera respuesta especializada vía Ollama."""

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
        return any(re.search(r"\b" + re.escape(k) + r"\b", q) for k in self.keywords)

    async def run(
        self,
        question: str,
        rag_fn: Callable,   # async fn(question, collection, limit) → list[dict]
        ollama_fn: Callable, # sync fn(question, context) → str
        loop: asyncio.AbstractEventLoop,
    ) -> AgentResult:
        # Buscar en todas las collections del agente
        all_chunks: list[dict] = []
        for col in self.collections:
            chunks = await rag_fn(question, col, limit=2)
            all_chunks.extend(chunks)

        # Deduplicar por contenido
        seen: set[str] = set()
        unique: list[dict] = []
        for c in all_chunks:
            key = c.get("content", "")[:60]
            if key not in seen:
                seen.add(key)
                unique.append(c)
        chunks = unique[:3]

        if not chunks:
            return AgentResult(agent=self.name, answer="", confidence=0.0)

        # Construir contexto especializado
        parts = [f"[{c['title']}]\n{c['content'][:300]}" for c in chunks]
        rag_context = "\n\n".join(parts)

        # Prompt especializado para el agente
        specialized_q = f"[{self.specialty}] {question}"
        try:
            answer = await loop.run_in_executor(None, ollama_fn, specialized_q, rag_context)
        except Exception as e:
            logger.warning("%s Ollama error: %s", self.name, e)
            # Fallback: primera línea del RAG
            answer = chunks[0]["content"].split("\n")[0].strip()[:200]

        confidence = min(1.0, 0.2 + len(chunks) / 3)
        sources = [c.get("source", c.get("title", "")) for c in chunks]
        return AgentResult(
            agent=self.name,
            answer=answer,
            confidence=confidence,
            sources=sources,
            chunks_used=len(chunks),
        )


# ── Queen ─────────────────────────────────────────────────────────────────────

class QueenAgent:
    """
    Orquestadora principal. Recibe pregunta, dispatcha a Workers relevantes
    en paralelo, consolida respuestas con consenso ponderado por confianza.
    """

    def __init__(self) -> None:
        self.workers: list[WorkerAgent] = [
            WorkerAgent(
                name="AgentFacturas",
                specialty="Especialista en CFDI, facturas, ingresos y egresos contables",
                collections=["fourgea_docs", "fiscal_mx"],
                keywords=_KW_FACTURAS,
            ),
            WorkerAgent(
                name="AgentNomina",
                specialty="Especialista en nómina, retenciones ISR, cuotas IMSS y empleados",
                collections=["fiscal_mx"],
                keywords=_KW_NOMINA,
            ),
            WorkerAgent(
                name="AgentIVA",
                specialty="Especialista en IVA, DIOT, acreditamiento y declaraciones fiscales",
                collections=["fourgea_docs", "fiscal_mx"],
                keywords=_KW_IVA,
            ),
        ]

    def _route(self, question: str) -> list[WorkerAgent]:
        """Selecciona workers relevantes. Si ninguno aplica → todos."""
        relevant = [w for w in self.workers if w.is_relevant(question)]
        return relevant if relevant else self.workers

    def _consolidate(self, results: list[AgentResult]) -> str:
        """Combina respuestas múltiples en una respuesta coherente."""
        valid = [r for r in results if r.answer and r.confidence > 0]
        if not valid:
            return "No encontré información suficiente para responder esta consulta."

        valid.sort(key=lambda r: r.confidence, reverse=True)
        if len(valid) == 1:
            return valid[0].answer

        # Agente principal (mayor confianza) + suplementos no redundantes
        primary = valid[0].answer
        primary_words = set(primary.lower().split())
        supplements = []
        for r in valid[1:]:
            if not r.answer:
                continue
            r_words = set(r.answer.lower().split())
            overlap = len(primary_words & r_words) / max(len(r_words), 1)
            if overlap < 0.6:  # Solo si aporta contenido nuevo (>40% diferente)
                first = r.answer.split(".")[0].strip()
                if len(first) > 20:
                    supplements.append(f"[{r.agent}] {first}.")

        if supplements:
            return primary + "\n\n" + "\n".join(supplements[:2])
        return primary

    async def run(
        self,
        question: str,
        rag_fn: Callable,
        ollama_fn: Callable,
    ) -> dict[str, Any]:
        """
        Ejecuta el swarm completo en paralelo.
        Retorna: answer, agents_used, confidences, total_chunks.
        """
        loop = asyncio.get_event_loop()
        workers = self._route(question)
        logger.info(
            "Queen routing '%s' → %s",
            question[:60],
            [w.name for w in workers],
        )

        tasks = [w.run(question, rag_fn, ollama_fn, loop) for w in workers]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        results = [r for r in raw_results if isinstance(r, AgentResult)]
        answer = self._consolidate(results)

        return {
            "answer": answer,
            "agents_used": [r.agent for r in results if r.answer],
            "confidences": {r.agent: round(r.confidence, 2) for r in results},
            "total_chunks": sum(r.chunks_used for r in results),
        }


# Singleton
queen = QueenAgent()
