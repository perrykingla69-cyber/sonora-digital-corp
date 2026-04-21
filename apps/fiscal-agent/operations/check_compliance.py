from datetime import datetime
from schemas.fiscal_responses import ComplianceCheckResult, ComplianceObligation
from rules import compliance_calendar


def check_compliance(regimen: str, month: int, year: int = None) -> ComplianceCheckResult:
    """Verifica obligaciones del régimen para mes/año."""

    if not year:
        year = datetime.now().year

    obligaciones_list = compliance_calendar.get_obligaciones_for_regime(regimen)
    obligaciones_result = []
    riesgos = []

    today = datetime.now()

    for ob in obligaciones_list:
        deadline_info = compliance_calendar.get_deadline_for_obligacion(
            ob['obligacion'], month, year
        )

        if not deadline_info:
            continue

        deadline = datetime.fromisoformat(deadline_info['deadline'])
        dias_restantes = (deadline - today).days

        riesgo = compliance_calendar.get_risk_level(dias_restantes)
        riesgos.append(riesgo)

        obligaciones_result.append(ComplianceObligation(
            obligacion=ob['obligacion'],
            deadline=deadline_info['deadline'],
            descripcion=ob['descripcion'],
            dias_restantes=dias_restantes,
            riesgo=riesgo
        ))

    # Riesgo general: rojo si alguno es rojo
    riesgo_general = "red" if "red" in riesgos else ("yellow" if "yellow" in riesgos else "green")

    proximo = min([o.deadline for o in obligaciones_result]) if obligaciones_result else None

    return ComplianceCheckResult(
        obligaciones=obligaciones_result,
        riesgo_general=riesgo_general,
        proximo_vencimiento=proximo
    )
