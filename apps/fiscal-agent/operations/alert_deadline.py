from datetime import datetime
from schemas.fiscal_responses import AlertDeadlineResult
from rules import compliance_calendar


def alert_deadline(obligacion: str, month: int = None, year: int = None) -> AlertDeadlineResult:
    """Calcula deadline exacto y fecha alerta para obligación."""

    if not month:
        today = datetime.now()
        month = today.month
    if not year:
        year = datetime.now().year

    deadline_info = compliance_calendar.get_deadline_for_obligacion(
        obligacion, month, year
    )

    if not deadline_info:
        # Fallback: obligation no encontrada, retornar genérico
        deadline_info = {
            'deadline': datetime(year, month, 17).isoformat(),
            'alert_date': datetime(year, month, 12).isoformat(),
            'dias_alerta': 5
        }

    deadline = datetime.fromisoformat(deadline_info['deadline'])
    alert_date = datetime.fromisoformat(deadline_info['alert_date'])
    dias_restantes = (deadline - datetime.now()).days

    return AlertDeadlineResult(
        obligacion=obligacion,
        deadline=deadline_info['deadline'],
        alerta_fecha=deadline_info['alert_date'],
        dias_restantes=dias_restantes
    )
