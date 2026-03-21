from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from ..core import legacy  # noqa: F401
from models import Factura  # type: ignore


def build_dashboard(db: Session, tenant_id: str) -> dict:
    now = datetime.now(timezone.utc)
    start_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    facturas = db.query(Factura).filter(Factura.tenant_id == tenant_id).all()
    month_items = [f for f in facturas if f.fecha_emision and f.fecha_emision.replace(tzinfo=timezone.utc) >= start_of_month]

    ingresos_mes = sum(f.total for f in month_items if f.tipo == "ingreso")
    gastos_mes = sum(f.total for f in month_items if f.tipo == "gasto")
    por_cobrar = sum(f.total for f in facturas if f.estado == "pendiente" and f.tipo == "ingreso")
    por_pagar = sum(f.total for f in facturas if f.estado == "pendiente" and f.tipo == "gasto")

    alertas = []
    if por_cobrar > 100000:
        alertas.append(f"Cuentas por cobrar altas: ${por_cobrar:,.2f} MXN")
    if por_pagar > por_cobrar * 0.8:
        alertas.append("Alerta: gastos pendientes cerca del nivel de ingresos")
    if ingresos_mes == 0:
        alertas.append("Sin ingresos registrados este mes")

    return {
        "tenant_id": tenant_id,
        "periodo": f"{now.year}-{now.month:02d}",
        "resumen": {
            "total_facturas": len(facturas),
            "facturas_mes": len(month_items),
            "ingresos_mes": ingresos_mes,
            "gastos_mes": gastos_mes,
            "utilidad_mes": ingresos_mes - gastos_mes,
            "por_cobrar": por_cobrar,
            "por_pagar": por_pagar,
        },
        "alertas": alertas,
        "kpis": {
            "margen_bruto_pct": round((ingresos_mes - gastos_mes) / ingresos_mes * 100, 2) if ingresos_mes > 0 else 0,
            "ratio_cobro_pago": round(por_cobrar / por_pagar, 2) if por_pagar > 0 else 0,
            "salud": "verde" if ingresos_mes > gastos_mes else "amarillo" if ingresos_mes > 0 else "rojo",
        },
    }
