from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..services.memory_service import get_memory_service
from packages.memory.mystic_memory import MemoryDocument, MemoryFeedback, MemorySearchRequest, MemorySearchResult

router = APIRouter(prefix="/api", tags=["Memory"])


class MemoryIngestRequest(BaseModel):
    key: str
    text: str
    metadata: dict = {}


@router.get("/memory/documents", response_model=list[MemoryDocument])
async def list_memory_documents(memory_service=Depends(get_memory_service)):
    return memory_service.list_documents()


@router.post("/memory/ingest", response_model=MemoryDocument)
async def ingest_memory_document(body: MemoryIngestRequest, memory_service=Depends(get_memory_service)):
    return memory_service.ingest(body.key, body.text, body.metadata)


@router.post("/rag/search", response_model=list[MemorySearchResult])
async def rag_search(body: MemorySearchRequest, memory_service=Depends(get_memory_service)):
    return memory_service.search(body.query, body.limit)


@router.post("/feedback/memory", response_model=MemoryFeedback)
async def memory_feedback(body: MemoryFeedback, memory_service=Depends(get_memory_service)):
    return memory_service.save_feedback(body.key, body.rating, body.comment)
