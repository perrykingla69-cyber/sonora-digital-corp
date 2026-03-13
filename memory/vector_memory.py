"""Vector memory scaffold for future embedding-based retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class VectorRecord:
    key: str
    text: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] | None = None


class VectorMemory:
    def __init__(self) -> None:
        self._records: list[VectorRecord] = []

    def add(self, key: str, text: str, embedding: list[float] | None = None, metadata: dict[str, Any] | None = None) -> None:
        self._records.append(VectorRecord(key=key, text=text, embedding=embedding, metadata=metadata or {}))

    def all(self) -> list[VectorRecord]:
        return list(self._records)

    def similarity_search(self, query: str, limit: int = 5) -> list[VectorRecord]:
        """Placeholder strategy: lexical search prior to full vector retrieval implementation."""
        matches = [record for record in self._records if query.lower() in record.text.lower()]
        return matches[:limit]
