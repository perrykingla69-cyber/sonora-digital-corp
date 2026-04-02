from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from ..services.memory_service import get_memory_service
from packages.memory.mystic_memory import (
    MemoryDocument,
    MemoryFeedback,
    MemoryFeedbackCreate,
    MemorySearchRequest,
    MemorySearchResult,
    MemoryService,
    MemoryStats,
)

router = APIRouter(prefix="/api", tags=["Memory"])
MemoryServiceDep = Annotated[MemoryService, Depends(get_memory_service)]


class MemoryIngestRequest(BaseModel):
    key: str
    text: str
    tenant_id: str | None = None
    kind: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.get("/memory/documents", response_model=list[MemoryDocument])
async def list_memory_documents(
    memory_service: MemoryServiceDep,
    tenant_id: str | None = Query(default=None),
    kind: str | None = Query(default=None),
    source: str | None = Query(default=None),
):
    return memory_service.list_documents(tenant_id=tenant_id, kind=kind, source=source)


@router.get("/memory/documents/{key}", response_model=MemoryDocument)
async def get_memory_document(key: str, memory_service: MemoryServiceDep):
    document = memory_service.get_document(key)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return document


@router.delete("/memory/documents/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory_document(key: str, memory_service: MemoryServiceDep):
    deleted = memory_service.delete_document(key)
    if not deleted:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/memory/ingest", response_model=MemoryDocument)
async def ingest_memory_document(body: MemoryIngestRequest, memory_service: MemoryServiceDep):
    return memory_service.ingest(body.key, body.text, body.metadata, tenant_id=body.tenant_id, kind=body.kind)


@router.get("/memory/stats", response_model=MemoryStats)
async def memory_stats(memory_service: MemoryServiceDep, tenant_id: str | None = Query(default=None)):
    return memory_service.stats(tenant_id=tenant_id)


@router.post("/rag/search", response_model=list[MemorySearchResult])
async def rag_search(body: MemorySearchRequest, memory_service: MemoryServiceDep):
    return memory_service.search(body.query, body.limit, tenant_id=body.tenant_id, kind=body.kind, source=body.source)


@router.post("/feedback/memory", response_model=MemoryFeedback)
async def memory_feedback(body: MemoryFeedbackCreate, memory_service: MemoryServiceDep):
    return memory_service.save_feedback(body.key, body.rating, body.comment)


@router.get("/feedback/memory/{key}", response_model=list[MemoryFeedback])
async def list_memory_feedback(key: str, memory_service: MemoryServiceDep):
    return memory_service.get_feedback(key)
