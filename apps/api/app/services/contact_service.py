from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core import legacy  # noqa: F401
from models import Contacto, Factura  # type: ignore


def create_contact(db: Session, tenant_id: str, body):
    contacto = Contacto(tenant_id=tenant_id, **body.model_dump())
    db.add(contacto)
    db.commit()
    db.refresh(contacto)
    return contacto


def list_contacts(db: Session, tenant_id: str, tipo: str | None, buscar: str | None):
    q = db.query(Contacto).filter(Contacto.tenant_id == tenant_id, Contacto.activo == True)
    if tipo:
        q = q.filter(Contacto.tipo == tipo)
    if buscar:
        term = f"%{buscar}%"
        q = q.filter(
            (Contacto.razon_social.ilike(term))
            | (Contacto.rfc.ilike(term))
            | (Contacto.contacto_nombre.ilike(term))
        )
    return q.order_by(Contacto.razon_social).all()


def get_contact(db: Session, tenant_id: str, contacto_id: str):
    contacto = db.query(Contacto).filter(Contacto.id == contacto_id, Contacto.tenant_id == tenant_id).first()
    if not contacto:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    ventas = db.query(func.sum(Factura.total), func.count(Factura.id)).filter(
        Factura.tenant_id == tenant_id,
        Factura.rfc_receptor == contacto.rfc,
        Factura.tipo == "ingreso",
    ).first()
    compras = db.query(func.sum(Factura.total), func.count(Factura.id)).filter(
        Factura.tenant_id == tenant_id,
        Factura.rfc_emisor == contacto.rfc,
        Factura.tipo == "gasto",
    ).first()
    contacto.monto_total_ventas = float(ventas[0] or 0)
    contacto.monto_total_compras = float(compras[0] or 0)
    contacto.total_facturas = int((ventas[1] or 0) + (compras[1] or 0))
    return contacto


def update_contact(db: Session, tenant_id: str, contacto_id: str, body: dict):
    contacto = db.query(Contacto).filter(Contacto.id == contacto_id, Contacto.tenant_id == tenant_id).first()
    if not contacto:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    for key, value in body.items():
        if hasattr(contacto, key):
            setattr(contacto, key, value)
    db.commit()
    db.refresh(contacto)
    return contacto


def deactivate_contact(db: Session, tenant_id: str, contacto_id: str):
    contacto = db.query(Contacto).filter(Contacto.id == contacto_id, Contacto.tenant_id == tenant_id).first()
    if not contacto:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    contacto.activo = False
    db.commit()
    return {"ok": True}
