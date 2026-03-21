from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class MemoryDocument(BaseModel):
    key: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MemorySearchRequest(BaseModel):
    query: str
    limit: int = Field(default=5, ge=1, le=25)


class MemorySearchResult(BaseModel):
    key: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float | None = None


class MemoryFeedbackCreate(BaseModel):
    key: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class MemoryFeedback(MemoryFeedbackCreate):
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MemoryStats(BaseModel):
    documents: int
    feedback_items: int
    vectors: int
    avg_feedback_rating: float | None = None
