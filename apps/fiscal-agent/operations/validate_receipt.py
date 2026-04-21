from schemas.fiscal_responses import ReceiptValidationResult
from rules import cfdi_rules


def validate_receipt(tipo: str, monto: float, rfc_emisor: str = None,
                     deducibilidad: str = None) -> ReceiptValidationResult:
    """Valida deducibilidad recibo/factura."""

    requisitos = []
    advertencias = []
    deductible = True

    # RFC requerido para deducción
    if not rfc_emisor:
        deductible = False
        requisitos.append("RFC del emisor (requerido para deducción)")
    elif not cfdi_rules.validate_rfc(rfc_emisor):
        deductible = False
        advertencias.append(f"RFC '{rfc_emisor}' inválido - revisar comprobante")

    # Monto razonable
    if monto <= 0:
        deductible = False
        requisitos.append("Monto debe ser positivo")

    # Tipo comprobante
    tipos_deductibles = ["factura", "cfdi", "recibo_honorarios"]
    if tipo not in tipos_deductibles:
        advertencias.append(f"Tipo '{tipo}' requiere validación adicional")

    # Requisitos generales
    requisitos.extend([
        "Comprobante con RFC emisor",
        "Concepto detallado (no genérico)",
        "Fecha dentro período fiscal"
    ])

    return ReceiptValidationResult(
        deductible=deductible,
        requisitos=requisitos,
        advertencias=advertencias
    )
