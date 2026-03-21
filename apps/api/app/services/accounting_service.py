from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from ..core import legacy  # noqa: F401
from calculos import calcular_iva  # type: ignore
from models import Factura  # type: ignore


def create_factura(db: Session, tenant_id: str, body):
    iva = body.iva if body.iva else calcular_iva(body.subtotal)
    total = body.total if body.total else (body.subtotal + iva)
    factura = Factura(
        tenant_id=tenant_id,
        folio=body.folio,
        uuid_cfdi=body.uuid_cfdi,
        rfc_emisor=body.rfc_emisor,
        rfc_receptor=body.rfc_receptor,
        nombre_emisor=body.nombre_emisor,
        nombre_receptor=body.nombre_receptor,
        subtotal=body.subtotal,
        iva=iva,
        total=total,
        tipo=body.tipo,
        moneda=body.moneda,
        tipo_cambio=body.tipo_cambio,
        estado=body.estado,
        concepto=body.concepto,
        fecha_emision=body.fecha_emision or datetime.utcnow(),
    )
    db.add(factura)
    db.commit()
    db.refresh(factura)
    return factura
