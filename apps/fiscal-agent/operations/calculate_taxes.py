from schemas.fiscal_requests import CalculateTaxesRequest
from schemas.fiscal_responses import TaxCalculationResult
from rules import tax_rules_2024 as tax_rules


def calculate_taxes(req: CalculateTaxesRequest) -> TaxCalculationResult:
    """Calcula ISR, IVA, IEPS determinístico contra tablas SAT 2024."""

    gastos = min(req.gastos, req.ingresos * tax_rules.deductible_limit_for_regime(req.regimen))
    base_gravable = req.ingresos - gastos

    if req.regimen == "PF_Honorarios":
        isr = tax_rules.calculate_isr_progressive(base_gravable)
    elif req.regimen in ["PM", "RIF"]:
        rate = tax_rules.get_isr_rate_for_regime(req.regimen)
        isr = base_gravable * rate
    else:
        isr = 0.0

    iva = tax_rules.calculate_iva(base_gravable, 0.16)
    ieps = 0.0

    total_impuestos = isr + iva + ieps

    return TaxCalculationResult(
        ingresos=round(req.ingresos, 2),
        gastos=round(req.gastos, 2),
        isr=round(isr, 2),
        iva=round(iva, 2),
        ieps=round(ieps, 2),
        base_gravable=round(base_gravable, 2),
        total_impuestos=round(total_impuestos, 2),
        fuente="LISR Art. 117, LIVA Art. 1 — SAT 2024"
    )
