from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from sqlalchemy import create_engine, text

from backend.app.ai.memory import KnowledgeStore, VectorMemory


@runtime_checkable
class DocumentStore(Protocol):
    def put(self, key: str, value: dict[str, Any]) -> None: ...
    def get(self, key: str, default: dict[str, Any] | None = None) -> dict[str, Any] | None: ...
    def keys(self) -> list[str]: ...
    def delete(self, key: str) -> bool: ...


@runtime_checkable
class FeedbackStore(Protocol):
    def put(self, key: str, value: list[dict[str, Any]]) -> None: ...
    def get(self, key: str, default: list[dict[str, Any]] | None = None) -> list[dict[str, Any]] | None: ...
    def keys(self) -> list[str]: ...


@runtime_checkable
class SearchAnalyticsStore(Protocol):
    def put(self, key: str, value: list[dict[str, Any]]) -> None: ...
    def get(self, key: str, default: list[dict[str, Any]] | None = None) -> list[dict[str, Any]] | None: ...


@runtime_checkable
class VectorStore(Protocol):
    def add(self, key: str, text: str, embedding: list[float] | None = None, metadata: dict[str, Any] | None = None) -> None: ...
    def similarity_search(self, query: str, limit: int = 5, query_embedding: list[float] | None = None) -> list[Any]: ...
    def get(self, key: str) -> Any | None: ...
    def delete(self, key: str) -> bool: ...


class JsonDocumentStore(KnowledgeStore):
    def __init__(self, persist_path: str | Path) -> None:
        super().__init__(str(persist_path))


class JsonFeedbackStore(KnowledgeStore):
    def __init__(self, persist_path: str | Path) -> None:
        super().__init__(str(persist_path))


class JsonSearchAnalyticsStore(KnowledgeStore):
    def __init__(self, persist_path: str | Path) -> None:
        super().__init__(str(persist_path))


class JsonVectorStore(VectorMemory):
    def __init__(self, persist_path: str | Path) -> None:
        super().__init__(str(persist_path))


class SqlAlchemyKVStore:
    def __init__(self, database_url: str, namespace: str) -> None:
        self.engine = create_engine(database_url)
        self.namespace = namespace
        self._ensure_table()

    def put(self, key: str, value: Any) -> None:
        payload = json.dumps(value)
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO memory_kv_store (namespace, key, value)
                    VALUES (:namespace, :key, :value)
                    ON CONFLICT(namespace, key)
                    DO UPDATE SET value = excluded.value
                    """
                ),
                {"namespace": self.namespace, "key": key, "value": payload},
            )

    def get(self, key: str, default: Any = None) -> Any:
        with self.engine.begin() as connection:
            row = connection.execute(
                text("SELECT value FROM memory_kv_store WHERE namespace = :namespace AND key = :key"),
                {"namespace": self.namespace, "key": key},
            ).fetchone()
        return json.loads(row[0]) if row else default

    def keys(self) -> list[str]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                text("SELECT key FROM memory_kv_store WHERE namespace = :namespace ORDER BY key"),
                {"namespace": self.namespace},
            ).fetchall()
        return [row[0] for row in rows]

    def delete(self, key: str) -> bool:
        with self.engine.begin() as connection:
            result = connection.execute(
                text("DELETE FROM memory_kv_store WHERE namespace = :namespace AND key = :key"),
                {"namespace": self.namespace, "key": key},
            )
        return result.rowcount > 0

    def _ensure_table(self) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS memory_kv_store (
                        namespace TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        PRIMARY KEY(namespace, key)
                    )
                    """
                )
            )


class PostgresDocumentStore(SqlAlchemyKVStore):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url, "documents")


class PostgresFeedbackStore(SqlAlchemyKVStore):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url, "feedback")


class PostgresSearchAnalyticsStore(SqlAlchemyKVStore):
    def __init__(self, database_url: str) -> None:
        super().__init__(database_url, "search_analytics")


class QdrantVectorStore:
    def __init__(self, url: str, collection_name: str = "mystic_memory") -> None:
        try:
            from qdrant_client import QdrantClient
        except ImportError as exc:
            raise RuntimeError("qdrant-client is required to use QdrantVectorStore") from exc

        self._client = QdrantClient(url=url)
        self.collection_name = collection_name
        self._fallback = VectorMemory()

    def add(self, key: str, text: str, embedding: list[float] | None = None, metadata: dict[str, Any] | None = None) -> None:
        # Keep a lexical fallback while the real embedding pipeline is wired in.
        self._fallback.add(key, text, embedding=embedding, metadata=metadata)

    def similarity_search(self, query: str, limit: int = 5, query_embedding: list[float] | None = None) -> list[Any]:
        return self._fallback.similarity_search(query, limit=limit, query_embedding=query_embedding)

    def get(self, key: str) -> Any | None:
        return self._fallback.get(key)

    def delete(self, key: str) -> bool:
        return self._fallback.delete(key)
