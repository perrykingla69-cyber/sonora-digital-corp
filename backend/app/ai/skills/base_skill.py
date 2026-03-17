"""Base skill class — all skills inherit from this."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any


class BaseSkill(ABC):
    """Standard callable interface for all skills."""

    name: str = "base"
    description: str = ""

    def __call__(self, **kwargs: Any) -> dict:
        try:
            result = self.execute(**kwargs)
            return {
                "skill": self.name,
                "status": "ok",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "result": result,
            }
        except Exception as exc:
            return {
                "skill": self.name,
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(exc),
            }

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Implement skill logic here."""
