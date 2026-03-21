from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..services.memory_service import get_memory_service
from packages.memory.mystic_memory import (
    MemoryDocument,
    MemoryFeedback,
    MemoryFeedbackCreate,
    MemorySearchRequest,
    MemorySearchResult,
    MemoryService,
)

router = APIRouter(prefix="/api", tags=["Memory"])
MemoryServiceDep = Annotated[MemoryService, Depends(get_memory_service)]


class MemoryIngestRequest(BaseModel):
    key: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.get("/memory/documents", response_model=list[MemoryDocument])
async def list_memory_documents(memory_service: MemoryServiceDep):
    return memory_service.list_documents()


@router.post("/memory/ingest", response_model=MemoryDocument)
async def ingest_memory_document(body: MemoryIngestRequest, memory_service: MemoryServiceDep):
    return memory_service.ingest(body.key, body.text, body.metadata)


@router.post("/rag/search", response_model=list[MemorySearchResult])
async def rag_search(body: MemorySearchRequest, memory_service: MemoryServiceDep):
    return memory_service.search(body.query, body.limit)


@router.post("/feedback/memory", response_model=MemoryFeedback)
async def memory_feedback(body: MemoryFeedbackCreate, memory_service: MemoryServiceDep):
    return memory_service.save_feedback(body.key, body.rating, body.comment)


@router.get("/feedback/memory/{key}", response_model=list[MemoryFeedback])
async def list_memory_feedback(key: str, memory_service: MemoryServiceDep):
    return memory_service.get_feedback(key)
