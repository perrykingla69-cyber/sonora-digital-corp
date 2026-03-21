from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core import legacy  # noqa: F401
from models import Empleado  # type: ignore


def _recalculate_salary_fields(payload: dict[str, Any]) -> dict[str, Any]:
    salary = payload.get("salario_mensual", 0.0) or 0.0
    factor = payload.get("factor_integracion", 1.0452) or 1.0452
    payload["salario_diario"] = round(salary / 30.4, 4)
    payload["salario_integrado"] = round(payload["salario_diario"] * factor, 4)
    return payload


def create_employee(db: Session, tenant_id: str, body):
    data = _recalculate_salary_fields(body.model_dump())
    empleado = Empleado(tenant_id=tenant_id, **data)
    db.add(empleado)
    db.commit()
    db.refresh(empleado)
    return empleado


def list_employees(db: Session, tenant_id: str, incluir_bajas: bool):
    q = db.query(Empleado).filter(Empleado.tenant_id == tenant_id)
    if not incluir_bajas:
        q = q.filter(Empleado.activo == True)
    return q.order_by(Empleado.nombre).all()


def get_employee(db: Session, tenant_id: str, empleado_id: str):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id, Empleado.tenant_id == tenant_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


def update_employee(db: Session, tenant_id: str, empleado_id: str, body: dict[str, Any]):
    empleado = get_employee(db, tenant_id, empleado_id)
    for key, value in body.items():
        if hasattr(empleado, key):
            setattr(empleado, key, value)
    if "salario_mensual" in body or "factor_integracion" in body:
        empleado.salario_diario = round((empleado.salario_mensual or 0.0) / 30.4, 4)
        factor = getattr(empleado, "factor_integracion", 1.0452) or 1.0452
        empleado.salario_integrado = round(empleado.salario_diario * factor, 4)
    db.commit()
    db.refresh(empleado)
    return empleado


def deactivate_employee(db: Session, tenant_id: str, empleado_id: str):
    empleado = get_employee(db, tenant_id, empleado_id)
    empleado.activo = False
    empleado.fecha_baja = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True, "mensaje": f"{empleado.nombre} dado de baja"}


def payroll_preview(db: Session, tenant_id: str, empleado_id: str, dias: int, percepciones_extra: float):
    empleado = get_employee(db, tenant_id, empleado_id)

    uma_2026 = 108.57
    smg_2026 = 278.80
    salario_bruto = round((empleado.salario_diario or 0) * dias + percepciones_extra, 2)
    salario_integrado_dia = empleado.salario_integrado or empleado.salario_diario or 0

    cuota_fija = round(uma_2026 * 0.204 * (dias / 30), 2)
    excedente_base = max(0, salario_integrado_dia - uma_2026 * 3) * dias
    cuota_excedente = round(excedente_base * 0.004, 2)
    invalidez_vida = round(salario_integrado_dia * dias * 0.00625, 2)
    cesantia = round(salario_integrado_dia * dias * 0.01125, 2)
    imss_trabajador = round(cuota_fija + cuota_excedente + invalidez_vida + cesantia, 2)

    em_mat_patron = round(salario_integrado_dia * dias * 0.1005, 2)
    riesgo_trabajo = round(salario_integrado_dia * dias * (empleado.prima_riesgo_trabajo or 0.005), 2)
    invalidez_patron = round(salario_integrado_dia * dias * 0.01750, 2)
    guarderias = round(salario_integrado_dia * dias * 0.01, 2)
    cesantia_patron = round(salario_integrado_dia * dias * 0.03150, 2)
    imss_patron = round(em_mat_patron + riesgo_trabajo + invalidez_patron + guarderias + cesantia_patron, 2)

    infonavit_patron = round(salario_integrado_dia * dias * 0.05, 2)
    infonavit_trabajador = 0.0
    if empleado.tiene_infonavit and empleado.descuento_infonavit:
        if empleado.tipo_descuento_infonavit == "vsm":
            infonavit_trabajador = round(empleado.descuento_infonavit * smg_2026, 2)
        elif empleado.tipo_descuento_infonavit == "porcentaje":
            infonavit_trabajador = round(salario_bruto * empleado.descuento_infonavit / 100, 2)
        else:
            infonavit_trabajador = empleado.descuento_infonavit

    isr = _calculate_isr_table(salario_bruto)
    subsidio = _calculate_subsidy(salario_bruto)
    isr_neto = max(0, isr - subsidio)
    caja_ahorro = round(salario_bruto * (empleado.caja_ahorro_pct or 0) / 100, 2)
    prestamos = empleado.prestamos or 0.0
    total_deducciones = round(imss_trabajador + isr_neto + infonavit_trabajador + caja_ahorro + prestamos, 2)
    salario_neto = round(salario_bruto - total_deducciones, 2)
    costo_empresa = round(salario_bruto + imss_patron + infonavit_patron, 2)

    return {
        "empleado": empleado.nombre,
        "puesto": empleado.puesto,
        "periodo_dias": dias,
        "percepciones": {
            "salario_bruto": salario_bruto,
            "percepciones_extra": percepciones_extra,
            "vales_despensa": empleado.vales_despensa or 0,
            "total": round(salario_bruto + (empleado.vales_despensa or 0), 2),
        },
        "deducciones_trabajador": {
            "imss": imss_trabajador,
            "isr_causado": isr,
            "subsidio_empleo": subsidio,
            "isr_neto": isr_neto,
            "infonavit_credito": infonavit_trabajador,
            "caja_ahorro": caja_ahorro,
            "prestamos": prestamos,
            "total": total_deducciones,
        },
        "cuotas_patronales": {
            "imss_patron": imss_patron,
            "infonavit_patron": infonavit_patron,
            "total": round(imss_patron + infonavit_patron, 2),
        },
        "salario_neto": salario_neto,
        "costo_total_empresa": costo_empresa,
        "info": {
            "uma_2026": uma_2026,
            "smg_2026": smg_2026,
            "salario_diario": empleado.salario_diario,
            "salario_integrado": empleado.salario_integrado,
            "factor_integracion": empleado.factor_integracion,
        },
    }


def _calculate_subsidy(salario: float) -> float:
    if salario <= 1768.96:
        return 407.02
    if salario <= 2653.38:
        return 406.83
    if salario <= 3472.84:
        return 406.62
    if salario <= 3537.87:
        return 392.77
    if salario <= 4446.15:
        return 382.46
    if salario <= 4717.18:
        return 354.23
    if salario <= 5335.42:
        return 324.87
    if salario <= 6224.67:
        return 294.63
    if salario <= 7113.90:
        return 253.54
    if salario <= 7382.33:
        return 217.61
    return 0.0


def _calculate_isr_table(salario: float) -> float:
    if salario <= 746.04:
        return round(salario * 0.0192, 2)
    if salario <= 6332.05:
        return round(salario * 0.0640, 2)
    if salario <= 11128.01:
        return round(salario * 0.1088, 2)
    if salario <= 12935.82:
        return round(salario * 0.16, 2)
    if salario <= 15487.71:
        return round(salario * 0.1792, 2)
    if salario <= 31236.49:
        return round(salario * 0.2136, 2)
    if salario <= 49233.00:
        return round(salario * 0.2352, 2)
    if salario <= 93993.90:
        return round(salario * 0.30, 2)
    return round(salario * 0.35, 2)
