import json
import os
from datetime import datetime, timedelta


def load_obligaciones():
    """Carga calendario obligaciones SAT."""
    here = os.path.dirname(__file__)
    with open(os.path.join(here, '../data/obligaciones_calendario.json')) as f:
        return json.load(f)


OBLIGACIONES = load_obligaciones()


def get_obligaciones_for_regime(regime: str) -> list:
    """Retorna obligaciones mensuales para régimen."""
    return OBLIGACIONES.get(regime, [])


def get_deadline_for_obligacion(obligacion: str, month: int, year: int) -> dict:
    """Calcula deadline exacto para obligación en mes/año dado."""
    for regime_obligaciones in OBLIGACIONES.values():
        for ob in regime_obligaciones:
            if ob['obligacion'] == obligacion:
                dia = ob['deadline_dia']
                if dia == 31:
                    # Último día del mes
                    next_month = datetime(year, month % 12 + 1 if month < 12 else 1,
                                        1) if month < 12 else datetime(year + 1, 1, 1)
                    deadline = next_month - timedelta(days=1)
                else:
                    deadline = datetime(year, month, min(dia, 28))  # Safe para feb

                alert_days = ob.get('días_alerta', 5)
                alert_date = deadline - timedelta(days=alert_days)

                return {
                    'obligacion': obligacion,
                    'deadline': deadline.isoformat(),
                    'alert_date': alert_date.isoformat(),
                    'dias_alerta': alert_days,
                    'descripcion': ob['descripcion']
                }

    return {}


def get_risk_level(days_remaining: int) -> str:
    """Determina nivel riesgo: red/yellow/green."""
    if days_remaining < 0:
        return "red"  # Vencida
    if days_remaining <= 3:
        return "red"  # Crítica
    if days_remaining <= 7:
        return "yellow"  # Atención
    return "green"
