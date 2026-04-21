import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from operations.calculate_taxes import calculate_taxes
from schemas.fiscal_requests import CalculateTaxesRequest


class TestCalculateTaxes:
    """Tests para cálculo de impuestos determinístico."""

    def test_pyme_pm_basic(self, sample_pyme):
        """PYME régimen PM: $150k ingresos, $50k gastos → ISR 30%."""
        req = CalculateTaxesRequest(**sample_pyme)
        result = calculate_taxes(req)

        assert result.ingresos == pytest.approx(150000)
        assert result.base_gravable == pytest.approx(100000)
        assert result.isr == pytest.approx(30000)  # 100k * 30%
        assert result.iva == pytest.approx(16000)  # 100k * 16%
        assert "LISR" in result.fuente

    def test_freelancer_progressive(self, sample_freelancer):
        """Freelancer PF_Honorarios: tabla progresiva ISR."""
        req = CalculateTaxesRequest(**sample_freelancer)
        result = calculate_taxes(req)

        assert result.base_gravable == pytest.approx(60000)  # 80k - 20k
        assert result.isr > 0
        assert result.isr < result.base_gravable * 0.30  # Menor que máximo
        assert "progresiva" not in result.fuente  # El fuente debe mencionar LISR

    @pytest.mark.parametrize("regimen,expected_rate", [
        ("PM", 0.30),
        ("RIF", 0.10),
    ])
    def test_fixed_rate_regimens(self, regimen, expected_rate):
        """Regímenes con tasa fija ISR."""
        req = CalculateTaxesRequest(
            ingresos=100000,
            gastos=20000,
            periodo="202406",
            regimen=regimen
        )
        result = calculate_taxes(req)
        base = 100000 - 20000
        expected_isr = base * expected_rate
        assert result.isr == pytest.approx(expected_isr, rel=0.01)

    def test_deduction_limit_respected(self):
        """No permite deducción mayor al límite del régimen."""
        req = CalculateTaxesRequest(
            ingresos=100000,
            gastos=100000,  # Intenta deducir 100%
            periodo="202406",
            regimen="PM"  # Límite 70%
        )
        result = calculate_taxes(req)
        max_deduction = 100000 * 0.70
        assert result.base_gravable >= 100000 - max_deduction

    def test_zero_income(self):
        """Ingresos cero → ISR cero."""
        req = CalculateTaxesRequest(
            ingresos=0.01,  # Casi cero
            gastos=0,
            periodo="202406",
            regimen="PM"
        )
        result = calculate_taxes(req)
        assert result.isr == pytest.approx(0, abs=1)  # <1 pesos

    def test_response_format(self, sample_pyme):
        """Response contiene campos requeridos."""
        req = CalculateTaxesRequest(**sample_pyme)
        result = calculate_taxes(req)

        assert hasattr(result, 'isr')
        assert hasattr(result, 'iva')
        assert hasattr(result, 'base_gravable')
        assert hasattr(result, 'total_impuestos')
        assert hasattr(result, 'fuente')
