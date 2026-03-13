"""Knowledge store — key-value store with JSON persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class KnowledgeStore:
    def __init__(self, persist_path: str | None = None) -> None:
        self._data: dict[str, Any] = {}
        self._path = Path(persist_path) if persist_path else None
        if self._path and self._path.exists():
            self._load()

    def put(self, key: str, value: Any) -> None:
        self._data[key] = value
        if self._path:
            self._save()

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def delete(self, key: str) -> bool:
        if key in self._data:
            del self._data[key]
            if self._path:
                self._save()
            return True
        return False

    def search(self, query: str) -> dict[str, Any]:
        """Simple key-contains search."""
        q = query.lower()
        return {k: v for k, v in self._data.items() if q in k.lower()}

    def keys(self) -> list[str]:
        return list(self._data.keys())

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w") as fh:
            json.dump(self._data, fh, indent=2)

    def _load(self) -> None:
        with self._path.open() as fh:
            self._data = json.load(fh)
