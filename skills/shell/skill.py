"""Shared skill module with a standard callable interface."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class Skill:
    """Standard callable skill wrapper used by agents and orchestrator."""

    name = "shell"

    def __call__(self, **kwargs: Any) -> dict:
        return self.execute(**kwargs)

    def execute(self, **kwargs: Any) -> dict:
        return {
            "skill": self.name,
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": kwargs,
        }
