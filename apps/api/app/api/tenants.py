from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core import legacy  # noqa: F401
from ..db.session import get_db
from models import Tenant  # type: ignore
from schemas import TenantCreate, TenantResponse  # type: ignore
from security import require_role  # type: ignore

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post("", response_model=TenantResponse)
async def crear_tenant(body: TenantCreate, db: Session = Depends(get_db)):
    if db.query(Tenant).filter(Tenant.rfc == body.rfc).first():
        raise HTTPException(status_code=400, detail="RFC ya registrado")
    tenant = Tenant(**body.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("", response_model=List[TenantResponse])
async def listar_tenants(current_user=Depends(require_role("admin")), db: Session = Depends(get_db)):
    return db.query(Tenant).filter(Tenant.activo == True).all()
