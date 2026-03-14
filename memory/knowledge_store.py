"""Simple in-memory key-value knowledge store."""

from __future__ import annotations

from typing import Any


class KnowledgeStore:
    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def put(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def search(self, query: str) -> dict[str, Any]:
        return {k: v for k, v in self._data.items() if query.lower() in k.lower()}
