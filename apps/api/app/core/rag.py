"""
RAG — Retrieval Augmented Generation
Conecta HERMES a Qdrant para respuestas con contexto real.
"""

import logging
from typing import Optional
from uuid import UUID

import httpx
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.core.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "hermes_knowledge"
VECTOR_SIZE = 768  # nomic-embed-text


def get_qdrant() -> AsyncQdrantClient:
    return AsyncQdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        api_key=settings.QDRANT_API_KEY or None,
        https=False,
    )


async def embed_text(text: str) -> Optional[list[float]]:
    """Genera embedding via Ollama (nomic-embed-text)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                f"{settings.OLLAMA_URL}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
            )
            r.raise_for_status()
            return r.json()["embedding"]
    except Exception as e:
        logger.warning(f"Ollama embed error: {e}")
        return None


async def ensure_collection(client: AsyncQdrantClient) -> None:
    """Crea la colección si no existe."""
    collections = await client.get_collections()
    names = [c.name for c in collections.collections]
    if COLLECTION_NAME not in names:
        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        logger.info(f"Colección {COLLECTION_NAME} creada")


async def search_context(
    query: str,
    tenant_id: UUID,
    limit: int = 3,
    score_threshold: float = 0.65,
) -> str:
    """
    Busca contexto relevante en Qdrant para la query del usuario.
    Retorna string formateado listo para inyectar en el system prompt.
    """
    vector = await embed_text(query)
    if not vector:
        return ""

    try:
        client = get_qdrant()
        await ensure_collection(client)

        results = await client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter={
                "must": [
                    {
                        "key": "tenant_id",
                        "match": {"value": str(tenant_id)},
                    }
                ]
            },
            with_payload=True,
        )
        await client.close()

        if not results:
            return ""

        chunks = []
        for r in results:
            payload = r.payload or {}
            source = payload.get("source", "base de conocimiento")
            text = payload.get("text", "")
            if text:
                chunks.append(f"[{source}]\n{text}")

        if not chunks:
            return ""

        return "CONTEXTO RELEVANTE:\n" + "\n\n".join(chunks)

    except Exception as e:
        logger.warning(f"RAG search error: {e}")
        return ""
