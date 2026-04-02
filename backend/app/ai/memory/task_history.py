"""Task history — append-only execution trace with JSON persistence."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class TaskRecord:
    task_id: str
    task: dict[str, Any]
    result: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TaskHistory:
    def __init__(self, persist_path: str | None = None) -> None:
        self._records: list[TaskRecord] = []
        self._path = Path(persist_path) if persist_path else None
        if self._path and self._path.exists():
            self._load()

    def store(self, task_id: str, task: dict[str, Any], result: dict[str, Any]) -> TaskRecord:
        record = TaskRecord(task_id=task_id, task=task, result=result)
        self._records.append(record)
        if self._path:
            self._save()
        return record

    def recent(self, limit: int = 10) -> list[TaskRecord]:
        return self._records[-limit:]

    def find(self, task_id: str) -> TaskRecord | None:
        return next((r for r in self._records if r.task_id == task_id), None)

    def all(self) -> list[TaskRecord]:
        return list(self._records)

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w") as fh:
            json.dump([asdict(r) for r in self._records], fh, indent=2)

    def _load(self) -> None:
        with self._path.open() as fh:
            data = json.load(fh)
        self._records = [TaskRecord(**d) for d in data]
