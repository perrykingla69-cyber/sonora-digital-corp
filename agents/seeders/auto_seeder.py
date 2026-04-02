"""
AUTO SEEDER — El sistema que se alimenta solo
Triggered por: nuevo tenant, cron semanal, MYSTIC discovery
"""

import asyncio
import httpx
import hashlib
from uuid import UUID
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    SparseVectorParams, SparseIndexParams,
)
from niche_registry import NICHE_REGISTRY, classify_niche, get_niche_sources
import os
import logging

logger = logging.getLogger(__name__)

QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


class AutoSeeder:
    def __init__(self):
        self.qdrant = AsyncQdrantClient(url=QDRANT_URL)

    # ── Embedding ─────────────────────────────────────────────
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Genera vectores densos con nomic-embed-text (Ollama local)."""
        async with httpx.AsyncClient(timeout=60) as client:
            vectors = []
            for text in texts:
                r = await client.post(
                    f"{OLLAMA_URL}/api/embeddings",
                    json={"model": EMBED_MODEL, "prompt": text},
                )
                vectors.append(r.json()["embedding"])
        return vectors

    # ── Chunking ──────────────────────────────────────────────
    def chunk_text(self, text: str, source: str) -> list[dict]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
            chunk = " ".join(words[i:i + CHUNK_SIZE])
            if len(chunk.strip()) < 50:
                continue
            chunks.append({
                "text": chunk,
                "source": source,
                "chunk_index": i // (CHUNK_SIZE - CHUNK_OVERLAP),
                "id": hashlib.md5(f"{source}:{i}".encode()).hexdigest(),
            })
        return chunks

    # ── Colección Qdrant ──────────────────────────────────────
    async def ensure_collection(self, name: str):
        collections = await self.qdrant.get_collections()
        existing = [c.name for c in collections.collections]
        if name not in existing:
            await self.qdrant.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                sparse_vectors_config={
                    "bm25": SparseVectorParams(
                        index=SparseIndexParams(on_disk=False)
                    )
                },
            )
            logger.info(f"Colección creada: {name}")

    # ── Upsert a Qdrant ───────────────────────────────────────
    async def upsert_chunks(self, collection: str, chunks: list[dict], metadata: dict):
        await self.ensure_collection(collection)
        texts = [c["text"] for c in chunks]
        vectors = await self.embed(texts)

        points = []
        for chunk, vector in zip(chunks, vectors):
            points.append(PointStruct(
                id=int(hashlib.md5(chunk["id"].encode()).hexdigest(), 16) % (2**63),
                vector={"default": vector},
                payload={
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "chunk_index": chunk["chunk_index"],
                    **metadata,
                },
            ))

        await self.qdrant.upsert(collection_name=collection, points=points)
        logger.info(f"Subidos {len(points)} chunks a {collection}")

    # ── Fetch fuente ──────────────────────────────────────────
    async def fetch_source(self, source: dict) -> str:
        """Descarga contenido de una fuente."""
        try:
            if source["type"] == "url":
                async with httpx.AsyncClient(timeout=30) as client:
                    r = await client.get(source["url"])
                    # Extracción básica de texto (mejorar con BeautifulSoup)
                    text = r.text[:50000]  # cap 50k chars
                    return text
            elif source["type"] == "rss":
                async with httpx.AsyncClient(timeout=30) as client:
                    r = await client.get(source["url"])
                    return r.text[:30000]
            # Para PDFs y NOMs → implementar con pdfplumber en siguiente versión
            return f"Fuente pendiente de implementar: {source['type']}"
        except Exception as e:
            logger.error(f"Error fetching {source}: {e}")
            return ""

    # ── SEED GLOBAL (nichos base) ─────────────────────────────
    async def seed_global_niche(self, niche: str):
        """Seed las colecciones globales de un nicho."""
        config = get_niche_sources(niche)
        logger.info(f"Iniciando seed global: {niche}")

        for source in config["sources"]:
            content = await self.fetch_source(source)
            if not content:
                continue

            chunks = self.chunk_text(content, source.get("url", source.get("id", "unknown")))
            for collection in config["collections"]:
                await self.upsert_chunks(
                    collection=collection,
                    chunks=chunks,
                    metadata={
                        "niche": niche,
                        "tenant_id": "global",
                        "domain": source.get("topic", niche),
                        "source_type": source["type"],
                    },
                )

        logger.info(f"Seed global completo: {niche}")

    # ── SEED TENANT (onboarding nuevo cliente) ─────────────────
    async def seed_tenant(self, tenant_id: str, business_description: str):
        """
        Triggered automáticamente cuando un nuevo tenant se registra.
        MYSTIC llama esto desde el onboarding flow.
        """
        niche = classify_niche(business_description)
        logger.info(f"Nuevo tenant {tenant_id} → nicho: {niche}")

        # 1. Asegurar que las colecciones globales existen
        config = get_niche_sources(niche)
        for collection in config["collections"]:
            await self.ensure_collection(collection)

        # 2. Crear colección privada del tenant
        tenant_collection = f"tenant_{tenant_id}"
        await self.ensure_collection(tenant_collection)

        # 3. Si el nicho es nuevo → seed global primero
        await self.seed_global_niche(niche)

        logger.info(f"Tenant {tenant_id} listo con nicho: {niche}")
        return {"niche": niche, "collections": config["collections"] + [tenant_collection]}

    # ── UPDATE SEMANAL (MYSTIC cron) ──────────────────────────
    async def weekly_update(self):
        """MYSTIC corre esto cada semana para mantener el conocimiento fresco."""
        logger.info("Iniciando actualización semanal de knowledge base...")
        for niche in NICHE_REGISTRY:
            if niche == "general":
                continue
            await self.seed_global_niche(niche)
        logger.info("Actualización semanal completada")


# Entry point para N8N webhook o cron
async def main():
    import sys
    seeder = AutoSeeder()

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "weekly":
            await seeder.weekly_update()
        elif command == "niche" and len(sys.argv) > 2:
            await seeder.seed_global_niche(sys.argv[2])
        elif command == "tenant" and len(sys.argv) > 3:
            await seeder.seed_tenant(sys.argv[2], sys.argv[3])
    else:
        await seeder.weekly_update()


if __name__ == "__main__":
    asyncio.run(main())
