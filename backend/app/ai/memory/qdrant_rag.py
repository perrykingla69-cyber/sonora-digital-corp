"""Qdrant RAG client — embeddings locales vía Ollama (nomic-embed-text).

Uso:
    rag = QdrantRAG()
    await rag.ensure_collection("fiscal_mx")
    await rag.upsert("fiscal_mx", "art-17-iva", "El IVA en México es del 16%...", {"fuente": "LIVA"})
    results = await rag.search("fiscal_mx", "¿cuál es la tasa del IVA?", limit=3)
"""

from __future__ import annotations

import hashlib
import logging
import os
from typing import Any

import httpx
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

logger = logging.getLogger(__name__)

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
VECTOR_SIZE = 768  # nomic-embed-text produce 768 dims


class QdrantRAG:
    def __init__(self) -> None:
        self._client = AsyncQdrantClient(url=QDRANT_URL)

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------

    async def embed(self, text: str) -> list[float]:
        """Genera embedding vía Ollama (100% local, sin costo)."""
        async with httpx.AsyncClient(timeout=30) as http:
            r = await http.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": EMBED_MODEL, "prompt": text},
            )
            r.raise_for_status()
        return r.json()["embedding"]

    # ------------------------------------------------------------------
    # Colecciones
    # ------------------------------------------------------------------

    async def ensure_collection(self, name: str) -> None:
        """Crea la colección si no existe."""
        existing = {c.name for c in await self._client.get_collections()}
        if name not in existing:
            await self._client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info("Colección Qdrant creada: %s", name)

    # ------------------------------------------------------------------
    # Escritura
    # ------------------------------------------------------------------

    async def upsert(
        self,
        collection: str,
        doc_id: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Inserta o actualiza un documento con su embedding."""
        await self.ensure_collection(collection)
        vector = await self.embed(text)
        point_id = int(hashlib.md5(doc_id.encode()).hexdigest(), 16) % (2**63)
        await self._client.upsert(
            collection_name=collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={"doc_id": doc_id, "text": text, **(metadata or {})},
                )
            ],
        )

    async def upsert_batch(
        self,
        collection: str,
        docs: list[dict],  # [{id, text, metadata?}]
    ) -> None:
        """Inserta múltiples documentos en batch."""
        await self.ensure_collection(collection)
        points = []
        for doc in docs:
            vector = await self.embed(doc["text"])
            point_id = int(hashlib.md5(doc["id"].encode()).hexdigest(), 16) % (2**63)
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={"doc_id": doc["id"], "text": doc["text"], **doc.get("metadata", {})},
                )
            )
        await self._client.upsert(collection_name=collection, points=points)

    # ------------------------------------------------------------------
    # Búsqueda
    # ------------------------------------------------------------------

    async def search(
        self,
        collection: str,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Búsqueda semántica. Devuelve lista de {text, score, metadata}."""
        query_vector = await self.embed(query)
        results = await self._client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
        )
        return [
            {
                "text": r.payload.get("text", ""),
                "score": r.score,
                "doc_id": r.payload.get("doc_id", ""),
                **{k: v for k, v in r.payload.items() if k not in ("text", "doc_id")},
            }
            for r in results
        ]

    async def delete(self, collection: str, doc_id: str) -> None:
        point_id = int(hashlib.md5(doc_id.encode()).hexdigest(), 16) % (2**63)
        await self._client.delete(
            collection_name=collection,
            points_selector=[point_id],
        )


# Instancia singleton para importar en routers
qdrant_rag = QdrantRAG()
