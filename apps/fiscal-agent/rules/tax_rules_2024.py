import json
import os


def load_tax_tables():
    """Carga tablas SAT 2024 embebidas."""
    here = os.path.dirname(__file__)
    with open(os.path.join(here, '../data/tax_tables_2024.json')) as f:
        return json.load(f)


TAX_TABLES = load_tax_tables()


def calculate_isr_progressive(base_gravable: float) -> float:
    """Calcula ISR persona física con tabla progresiva 2024."""
    tablas = TAX_TABLES['isr']['tablas_progresivas']['2024']

    for tramo in tablas:
        if 'tarifa' not in tramo:
            continue
        desde = tramo['desde']
        hasta = tramo.get('hasta', float('inf'))

        if desde <= base_gravable <= hasta:
            excedente = base_gravable - desde
            return (excedente * tramo['tarifa']) + tramo['cuota_fija']

    return 0.0


def calculate_isr_corporate(utilidad: float) -> float:
    """Calcula ISR persona moral (tasa fija 30%)."""
    return utilidad * TAX_TABLES['isr']['personas_morales']['tasa_fija']


def calculate_iva(base: float, tasa: float = 0.16) -> float:
    """Calcula IVA. Tasa default: 16%."""
    # Tasas pueden estar como porcentajes (16) o decimales (0.16)
    tasas_validas = TAX_TABLES['iva']['tasas']
    tasa_normalizada = tasa if tasa < 1 else tasa / 100

    tasas_decimales = [t / 100 if t > 1 else t for t in tasas_validas]
    if tasa_normalizada not in tasas_decimales:
        raise ValueError(f"Tasa IVA {tasa} no válida. Válidas: {tasas_decimales}")
    return base * tasa_normalizada


def deductible_limit_for_regime(regime: str) -> float:
    """Límite de deducción por régimen."""
    limits = {
        "PM": 0.70,
        "PF_Honorarios": 0.50,
        "RIF": 0.60,
    }
    return limits.get(regime, 0.0)


def get_isr_rate_for_regime(regime: str) -> float:
    """Tasa ISR fija por régimen (para PM/RIF)."""
    rates = {
        "PM": 0.30,
        "RIF": 0.10,
        "PF_Honorarios": 0.25,
    }
    return rates.get(regime, 0.0)
