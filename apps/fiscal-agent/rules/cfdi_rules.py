import re

RFC_PATTERN = r"^[A-ZÑ&]{3,4}\d{6}[A-V0-9]{3}$"
CURP_PATTERN = r"^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$"


def validate_rfc(rfc: str) -> bool:
    """Valida formato RFC3757."""
    return bool(re.match(RFC_PATTERN, rfc.upper()))


def validate_curp(curp: str) -> bool:
    """Valida formato CURP."""
    return bool(re.match(CURP_PATTERN, curp.upper()))


def validate_iva_rate(rate: float) -> bool:
    """Valida tasa IVA válida: 0, 8, 16%."""
    return rate in [0.0, 0.08, 0.16]


def validate_ieps_rate(rate: float, producto: str = "") -> bool:
    """Valida tasa IEPS."""
    ieps_rates = {
        "gasolina": [0.381],
        "diesel": [0.341],
        "alcoholes": [0.06, 0.08, 0.12, 0.16]
    }
    if producto in ieps_rates:
        return rate in ieps_rates[producto]
    return False


def validate_cfdi_amount(amount: float) -> bool:
    """Montos válidos: positivos, hasta 2 decimales."""
    return amount > 0 and round(amount, 2) == amount


def validate_rfc_format_error(rfc: str) -> str:
    """Retorna mensaje error si RFC inválido."""
    if not rfc:
        return "RFC requerido"
    if not re.match(RFC_PATTERN, rfc.upper()):
        return f"RFC '{rfc}' no cumple formato RFC3757 (4 letras + 6 números + 3 alfanuméricos)"
    return ""


def validate_date_range(fecha_str: str, rango_start: str, rango_end: str) -> bool:
    """Valida que fecha esté en rango."""
    try:
        from datetime import datetime
        fecha = datetime.fromisoformat(fecha_str)
        start = datetime.fromisoformat(rango_start)
        end = datetime.fromisoformat(rango_end)
        return start <= fecha <= end
    except:
        return False
