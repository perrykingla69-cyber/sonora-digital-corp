from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core import legacy  # noqa: F401
from ..db.session import get_db
from ..services.accounting_service import create_factura
from models import Factura  # type: ignore
from schemas import FacturaCreate, FacturaResponse  # type: ignore
from security import get_current_user  # type: ignore

router = APIRouter(prefix="/facturas", tags=["Facturas"])


@router.post("", response_model=FacturaResponse)
async def crear_factura(body: FacturaCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_id = current_user.tenant_id if hasattr(current_user, "tenant_id") else current_user.get("tenant_id")
    return create_factura(db, tenant_id, body)


@router.get("", response_model=List[FacturaResponse])
async def listar_facturas(
    tipo: Optional[str] = Query(None, description="ingreso | gasto"),
    estado: Optional[str] = Query(None, description="pendiente | pagada | cancelada"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenant_id = current_user.tenant_id if hasattr(current_user, "tenant_id") else current_user.get("tenant_id")
    q = db.query(Factura).filter(Factura.tenant_id == tenant_id)
    if tipo:
        q = q.filter(Factura.tipo == tipo)
    if estado:
        q = q.filter(Factura.estado == estado)
    return q.order_by(Factura.fecha_emision.desc()).offset(offset).limit(limit).all()


@router.get("/{factura_id}", response_model=FacturaResponse)
async def obtener_factura(factura_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    tenant_id = current_user.tenant_id if hasattr(current_user, "tenant_id") else current_user.get("tenant_id")
    factura = db.query(Factura).filter(Factura.id == factura_id, Factura.tenant_id == tenant_id).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura
