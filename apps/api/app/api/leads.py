from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..services.lead_service import create_lead, delete_lead, list_leads, update_lead
from security import require_role  # type: ignore


from ..schemas import LeadCreate, LeadUpdate

router = APIRouter(tags=["CRM"])


@router.get("/leads")
async def listar_leads_endpoint(
    estado: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("contador", "ceo", "admin")),
):
    return list_leads(db, str(current_user.tenant_id), estado, limit)


@router.post("/leads", status_code=201)
async def crear_lead_endpoint(
    body: LeadCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("contador", "ceo", "admin")),
):
    return create_lead(db, str(current_user.tenant_id), body.model_dump(exclude_none=True))


@router.patch("/leads/{lead_id}")
async def actualizar_lead_endpoint(
    lead_id: str,
    body: LeadUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("contador", "ceo", "admin")),
):
    return update_lead(db, str(current_user.tenant_id), lead_id, body.model_dump(exclude_none=True))


@router.delete("/leads/{lead_id}")
async def eliminar_lead_endpoint(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("ceo", "admin")),
):
    return delete_lead(db, str(current_user.tenant_id), lead_id)
