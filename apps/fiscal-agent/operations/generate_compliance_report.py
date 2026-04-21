from datetime import datetime
from schemas.fiscal_responses import ComplianceReportResult
from rules import compliance_calendar
import json
import os


def generate_compliance_report(period: str, regimen: str) -> ComplianceReportResult:
    """Genera reporte ejecutivo cumplimiento fiscal."""

    # Parse period YYYYMM
    year = int(period[:4])
    month = int(period[4:6])

    obligaciones = compliance_calendar.get_obligaciones_for_regime(regimen)
    obligaciones_cumplidas = []
    obligaciones_pendientes = []
    riesgos = []

    today = datetime.now()

    for ob in obligaciones:
        deadline_info = compliance_calendar.get_deadline_for_obligacion(
            ob['obligacion'], month, year
        )
        if not deadline_info:
            continue

        deadline = datetime.fromisoformat(deadline_info['deadline'])
        dias_restantes = (deadline - today).days

        riesgo = compliance_calendar.get_risk_level(dias_restantes)
        riesgos.append(riesgo)

        if dias_restantes < 0:
            obligaciones_cumplidas.append(ob['obligacion'])
        else:
            obligaciones_pendientes.append(ob['obligacion'])

    resumen = f"Período {period}: {len(obligaciones_cumplidas)} cumplidas, {len(obligaciones_pendientes)} pendientes."
    riesgo_general = "red" if "red" in riesgos else ("yellow" if "yellow" in riesgos else "green")

    return ComplianceReportResult(
        periodo=period,
        regimen=regimen,
        resumen=resumen,
        obligaciones_cumplidas=obligaciones_cumplidas,
        obligaciones_pendientes=obligaciones_pendientes,
        riesgo=riesgo_general
    )
