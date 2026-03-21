from functools import lru_cache

from ..core.settings import get_settings
from packages.memory.mystic_memory import (
    MemoryService,
    PostgresDocumentStore,
    PostgresFeedbackStore,
    PostgresSearchAnalyticsStore,
    QdrantVectorStore,
)


@lru_cache(maxsize=1)
def get_memory_service() -> MemoryService:
    settings = get_settings()
    if settings.memory_backend == "postgres_qdrant":
        if not settings.memory_sqlalchemy_url:
            raise RuntimeError("MEMORY_SQLALCHEMY_URL is required when MEMORY_BACKEND=postgres_qdrant")
        if not settings.memory_qdrant_url:
            raise RuntimeError("MEMORY_QDRANT_URL is required when MEMORY_BACKEND=postgres_qdrant")
        return MemoryService(
            data_dir=settings.memory_data_dir,
            documents=PostgresDocumentStore(settings.memory_sqlalchemy_url),
            feedback=PostgresFeedbackStore(settings.memory_sqlalchemy_url),
            search_analytics=PostgresSearchAnalyticsStore(settings.memory_sqlalchemy_url),
            vectors=QdrantVectorStore(settings.memory_qdrant_url, collection_name=settings.memory_qdrant_collection),
        )
    return MemoryService(data_dir=settings.memory_data_dir)
