"""Task history store for orchestration traces."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class TaskRecord:
    task_id: str
    task: dict[str, Any]
    result: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TaskHistory:
    def __init__(self) -> None:
        self._records: list[TaskRecord] = []

    def store(self, task_id: str, task: dict[str, Any], result: dict[str, Any]) -> TaskRecord:
        record = TaskRecord(task_id=task_id, task=task, result=result)
        self._records.append(record)
        return record

    def recent(self, limit: int = 10) -> list[TaskRecord]:
        return self._records[-limit:]
