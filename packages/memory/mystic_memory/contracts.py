from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field


class MemoryDocument(BaseModel):
    key: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MemorySearchRequest(BaseModel):
    query: str
    limit: int = 5


class MemorySearchResult(BaseModel):
    key: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: Optional[float] = None


class MemoryFeedback(BaseModel):
    key: str
    rating: int
    comment: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
