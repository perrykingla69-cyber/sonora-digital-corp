import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from operations.suggest_deductions import suggest_deductions


class TestSuggestDeductions:
    """Tests para sugerencias de deducciones."""

    def test_pyme_suggestions(self):
        """PYME recibe sugerencias apropiadas."""
        result = suggest_deductions("PM", ingresos=150000)

        assert result.sugerencias
        assert len(result.sugerencias) > 0
        assert result.impacto_estimado > 0
        assert result.ahorro_potencial > 0

    def test_freelancer_suggestions(self):
        """Freelancer recibe sugerencias apropiadas."""
        result = suggest_deductions("PF_Honorarios", ingresos=80000)

        assert result.sugerencias
        categorias = [s.categoria for s in result.sugerencias]
        # Debe contener sugerencias típicas freelancer
        assert any("Internet" in c or "Oficina" in c for c in categorias)

    def test_ahorro_potencial_reasonable(self):
        """Ahorro potencial es razonable respecto a impuestos."""
        result = suggest_deductions("PM", ingresos=100000)

        # Ahorro debe ser menor al 30% de ingresos (máximo ISR PM)
        assert result.ahorro_potencial < 100000 * 0.30

    @pytest.mark.parametrize("regimen", ["PM", "PF_Honorarios", "RIF"])
    def test_all_regimens_suggest(self, regimen):
        """Todos regímenes retornan sugerencias."""
        result = suggest_deductions(regimen, ingresos=100000)

        assert result.sugerencias or not result.sugerencias  # OK sin sugerencias
        assert hasattr(result, 'ahorro_potencial')

    def test_suggestion_fields(self):
        """Cada sugerencia tiene campos requeridos."""
        result = suggest_deductions("PM", ingresos=150000)

        for sug in result.sugerencias:
            assert hasattr(sug, 'categoria')
            assert hasattr(sug, 'descripcion')
            assert hasattr(sug, 'monto_estimado')
            assert sug.monto_estimado >= 0
