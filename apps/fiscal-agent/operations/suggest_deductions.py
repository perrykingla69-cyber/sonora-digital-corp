from schemas.fiscal_responses import SuggestDeductionsResult, DeductionSuggestion
from rules import deduction_rules


def suggest_deductions(regimen: str, ingresos: float, gastos_actuales: float = 0) -> SuggestDeductionsResult:
    """Sugiere deducciones típicas por régimen."""

    sugerencias_raw = deduction_rules.suggest_deductions_for_regime(regimen, ingresos)
    sugerencias = [
        DeductionSuggestion(
            categoria=s['categoria'],
            descripcion=f"Deducción típica {regimen}: {s['categoria']}",
            monto_estimado=s['monto_estimado']
        )
        for s in sugerencias_raw
    ]

    # Impacto: ahorro en ISR por deductiones
    total_deductible = sum(s.monto_estimado for s in sugerencias)
    tasa_isr = {"PM": 0.30, "PF_Honorarios": 0.25, "RIF": 0.10}.get(regimen, 0.25)
    ahorro_potencial = total_deductible * tasa_isr

    return SuggestDeductionsResult(
        sugerencias=sugerencias,
        impacto_estimado=round(total_deductible, 2),
        ahorro_potencial=round(ahorro_potencial, 2)
    )
