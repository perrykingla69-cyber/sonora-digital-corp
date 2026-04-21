DEDUCTION_SUGGESTIONS = {
    "PM": [
        {"categoria": "Servicios Profesionales", "porcentaje": 0.08, "requisitos": ["Contrato", "RFC emisor"]},
        {"categoria": "Renta", "porcentaje": 0.15, "requisitos": ["Comprobante", "Contrato"]},
        {"categoria": "Servicios Técnicos", "porcentaje": 0.05, "requisitos": ["Factura", "RFC"]},
        {"categoria": "Combustible", "porcentaje": 0.10, "requisitos": ["Factura", "Registro"]},
        {"categoria": "Mantenimiento", "porcentaje": 0.06, "requisitos": ["Comprobante"]},
    ],
    "PF_Honorarios": [
        {"categoria": "Oficina en casa", "porcentaje": 0.05, "requisitos": ["Registro"]},
        {"categoria": "Internet/Telefonía", "porcentaje": 0.02, "requisitos": ["Recibo"]},
        {"categoria": "Software/Suscripciones", "porcentaje": 0.03, "requisitos": ["Factura"]},
        {"categoria": "Material de Oficina", "porcentaje": 0.01, "requisitos": ["Recibo"]},
        {"categoria": "Educación Continua", "porcentaje": 0.04, "requisitos": ["Constancia"]},
    ],
    "RIF": [
        {"categoria": "Compra de Mercancía", "porcentaje": 0.60, "requisitos": ["CFDI"]},
        {"categoria": "Servicios Básicos", "porcentaje": 0.05, "requisitos": ["Recibo"]},
        {"categoria": "Mantenimiento Equipo", "porcentaje": 0.10, "requisitos": ["Factura"]},
    ],
}


def suggest_deductions_for_regime(regime: str, ingresos: float) -> list:
    """Sugiere deducciones típicas por régimen e ingreso."""
    sugerencias = []
    if regime not in DEDUCTION_SUGGESTIONS:
        return sugerencias

    for deduction in DEDUCTION_SUGGESTIONS[regime]:
        monto_estimado = ingresos * deduction['porcentaje']
        sugerencias.append({
            "categoria": deduction['categoria'],
            "monto_estimado": round(monto_estimado, 2),
            "requisitos": deduction['requisitos'],
            "porcentaje": deduction['porcentaje']
        })

    return sorted(sugerencias, key=lambda x: x['monto_estimado'], reverse=True)


def get_deduction_requirements(categoria: str) -> list:
    """Retorna requisitos para tipo deducción."""
    for regime_deducciones in DEDUCTION_SUGGESTIONS.values():
        for deduction in regime_deducciones:
            if deduction['categoria'] == categoria:
                return deduction['requisitos']
    return []
