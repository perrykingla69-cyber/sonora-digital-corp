"""Vector memory — embedding-based semantic retrieval (pgvector-ready scaffold)."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class VectorRecord:
    key: str
    text: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorMemory:
    def __init__(self, persist_path: str | None = None) -> None:
        self._records: list[VectorRecord] = []
        self._path = Path(persist_path) if persist_path else None
        if self._path and self._path.exists():
            self._load()

    def add(
        self,
        key: str,
        text: str,
        embedding: list[float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        # Replace if key exists
        self._records = [r for r in self._records if r.key != key]
        self._records.append(VectorRecord(key=key, text=text, embedding=embedding, metadata=metadata or {}))
        if self._path:
            self._save()

    def all(self) -> list[VectorRecord]:
        return list(self._records)

    def get(self, key: str) -> VectorRecord | None:
        return next((r for r in self._records if r.key == key), None)

    def similarity_search(self, query: str, limit: int = 5, query_embedding: list[float] | None = None) -> list[VectorRecord]:
        """
        If query_embedding is provided → cosine similarity ranking.
        Otherwise → lexical (substring) fallback.
        """
        if query_embedding:
            scored = [
                (r, _cosine(query_embedding, r.embedding))
                for r in self._records
                if r.embedding and len(r.embedding) == len(query_embedding)
            ]
            scored.sort(key=lambda x: x[1], reverse=True)
            return [r for r, _ in scored[:limit]]

        # Lexical fallback
        q = query.lower()
        matches = [r for r in self._records if q in r.text.lower()]
        return matches[:limit]

    def delete(self, key: str) -> bool:
        before = len(self._records)
        self._records = [r for r in self._records if r.key != key]
        if len(self._records) < before:
            if self._path:
                self._save()
            return True
        return False

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w") as fh:
            json.dump([asdict(r) for r in self._records], fh, indent=2)

    def _load(self) -> None:
        with self._path.open() as fh:
            data = json.load(fh)
        self._records = [VectorRecord(**d) for d in data]
