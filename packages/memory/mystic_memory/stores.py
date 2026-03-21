from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

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


class JsonVectorStore(VectorMemory):
    def __init__(self, persist_path: str | Path) -> None:
        super().__init__(str(persist_path))
