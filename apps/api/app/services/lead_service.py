from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core import legacy  # noqa: F401
from models import Lead  # type: ignore


def list_leads(db: Session, tenant_id: str, estado: str | None, limit: int):
    q = db.query(Lead).filter(Lead.tenant_id == tenant_id)
    if estado:
        q = q.filter(Lead.status == estado)
    leads = q.order_by(Lead.created_at.desc()).limit(min(limit, 200)).all()
    return [
        {
            "id": lead.id,
            "nombre": lead.nombre,
            "empresa": lead.empresa,
            "email": lead.email,
            "telefono": lead.telefono,
            "estado": lead.status,
            "notas": lead.notas,
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
        }
        for lead in leads
    ]


def create_lead(db: Session, tenant_id: str, body: dict):
    status = body.pop("estado", None) or body.pop("status", None) or "nuevo"
    lead = Lead(tenant_id=tenant_id, status=status, **body)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return {"ok": True, "id": lead.id, "nombre": lead.nombre}


def update_lead(db: Session, tenant_id: str, lead_id: str, body: dict):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.tenant_id == tenant_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    payload = body.copy()
    if "estado" in payload:
        payload["status"] = payload.pop("estado")
    for campo, valor in payload.items():
        if hasattr(lead, campo):
            setattr(lead, campo, valor)
    db.commit()
    return {"ok": True, "id": lead.id, "estado": lead.status}


def delete_lead(db: Session, tenant_id: str, lead_id: str):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.tenant_id == tenant_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    db.delete(lead)
    db.commit()
    return {"ok": True}
