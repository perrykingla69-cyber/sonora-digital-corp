"""
ModelRouter — 4-layer cost optimization for HERMES OS
Layer 0: Redis cache
Layer 1: RAG-only if confidence >0.9
Layer 2: Free tier by complexity
Layer 3: Paid model
"""
import hashlib
import json
import logging
import os
from dataclasses import dataclass
from typing import Optional
import redis

logger = logging.getLogger(__name__)

FREE_MODELS = {
    "simple": "google/gemini-flash-1.5:free",
    "fiscal": "deepseek/deepseek-r1:free",
    "legal": "meta-llama/llama-3.3-70b:free",
    "music": "google/gemini-flash-1.5:free",
}
PAID_MODEL = "google/gemini-2.0-flash-001"


@dataclass
class RouteDecision:
    model: str
    use_cache: bool
    rag_only: bool
    estimated_cost_usd: float
    reason: str


class ModelRouter:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.r = redis.from_url(redis_url, decode_responses=True)

    def _cache_key(self, tenant_id: str, query: str) -> str:
        h = hashlib.md5(f"{tenant_id}:{query}".encode()).hexdigest()
        return f"model_cache:{h}"

    def get_cached(self, tenant_id: str, query: str) -> Optional[str]:
        return self.r.get(self._cache_key(tenant_id, query))

    def set_cached(self, tenant_id: str, query: str, response: str, ttl: int = 3600):
        self.r.setex(self._cache_key(tenant_id, query), ttl, response)

    def _classify_complexity(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ["impuesto", "cfdi", "sat", "isr", "iva", "deducción"]):
            return "fiscal"
        if any(w in q for w in ["contrato", "legal", "ley", "demanda", "notario"]):
            return "legal"
        if any(w in q for w in ["canción", "música", "artista", "sello", "spotify", "tiktok"]):
            return "music"
        return "simple"

    def route(self, query: str, tenant_id: str, rag_confidence: float = 0.0) -> RouteDecision:
        # Layer 1: RAG-only if high confidence
        if rag_confidence >= 0.9:
            return RouteDecision(model="rag_only", use_cache=False, rag_only=True, estimated_cost_usd=0.0, reason="RAG confidence ≥0.9 — no LLM needed")

        # Layer 2: free tier
        complexity = self._classify_complexity(query)
        if complexity in FREE_MODELS:
            return RouteDecision(model=FREE_MODELS[complexity], use_cache=False, rag_only=False, estimated_cost_usd=0.0, reason=f"Free model — {complexity} query")

        # Layer 3: paid
        return RouteDecision(model=PAID_MODEL, use_cache=False, rag_only=False, estimated_cost_usd=0.000075, reason="Paid model — complex query")
