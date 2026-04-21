from schemas.fiscal_responses import CFDIValidationResult, CFDIValidationError
from rules import cfdi_rules


def validate_cfdi(xml_content: str = None, json_content: dict = None) -> CFDIValidationResult:
    """Valida CFDI 4.0 contra catálogos SAT."""

    errors = []

    # Parse JSON si viene en XML (simplificado para MVP)
    if not json_content and xml_content:
        try:
            import json as json_lib
            json_content = json_lib.loads(xml_content)
        except:
            errors.append(CFDIValidationError(
                field="xml_content",
                error="No es JSON válido"
            ))
            return CFDIValidationResult(valid=False, errors=errors)

    if not json_content:
        errors.append(CFDIValidationError(field="content", error="CFDI vacío"))
        return CFDIValidationResult(valid=False, errors=errors)

    # Validaciones estructurales
    rfc_emisor = json_content.get("RFC_Emisor", "")
    rfc_receptor = json_content.get("RFC_Receptor", "")
    montos = json_content.get("Montos", {})

    # RFC validación
    if not cfdi_rules.validate_rfc(rfc_emisor):
        errors.append(CFDIValidationError(
            field="RFC_Emisor",
            error=cfdi_rules.validate_rfc_format_error(rfc_emisor)
        ))

    if not cfdi_rules.validate_rfc(rfc_receptor):
        errors.append(CFDIValidationError(
            field="RFC_Receptor",
            error=cfdi_rules.validate_rfc_format_error(rfc_receptor)
        ))

    # Validar tasas IVA
    for concepto in json_content.get("Conceptos", []):
        iva_rate = concepto.get("TasaIVA", 0.16)
        if not cfdi_rules.validate_iva_rate(iva_rate):
            errors.append(CFDIValidationError(
                field="TasaIVA",
                error=f"Tasa {iva_rate} no válida. Válidas: 0, 8, 16"
            ))

    # Validar montos positivos
    for key, valor in montos.items():
        if valor < 0:
            errors.append(CFDIValidationError(
                field=key,
                error=f"{key} debe ser positivo"
            ))

    return CFDIValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        version="4.0"
    )
