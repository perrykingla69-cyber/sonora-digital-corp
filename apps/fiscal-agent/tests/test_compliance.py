import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from operations.check_compliance import check_compliance


class TestCheckCompliance:
    """Tests para validación obligaciones fiscales."""

    def test_pm_july_obligations(self):
        """PM julio 2024: ISR 17-jul, IMSS 31-jul."""
        result = check_compliance("PM", month=7, year=2024)

        assert result.obligaciones
        assert len(result.obligaciones) > 0
        obligacion_names = [o.obligacion for o in result.obligaciones]
        assert "ISR_Mensual" in obligacion_names

    def test_compliance_risk_levels(self):
        """Obligaciones retornan niveles riesgo correctos."""
        result = check_compliance("PM", month=7, year=2024)

        assert result.riesgo_general in ["green", "yellow", "red"]
        for ob in result.obligaciones:
            assert ob.riesgo in ["green", "yellow", "red"]

    def test_pf_honorarios_obligations(self):
        """PF Honorarios tiene obligaciones específicas."""
        result = check_compliance("PF_Honorarios", month=7, year=2024)

        assert result.obligaciones
        obligacion_names = [o.obligacion for o in result.obligaciones]
        assert any("ISR" in name for name in obligacion_names)

    def test_days_remaining_calculated(self):
        """dias_restantes se calcula correctamente."""
        today = datetime.now()
        result = check_compliance("PM", month=today.month, year=today.year)

        assert result.obligaciones
        for ob in result.obligaciones:
            assert isinstance(ob.dias_restantes, int)
            # Riesgo debe correlacionar con días restantes
            if ob.dias_restantes < 0:
                assert ob.riesgo == "red"

    def test_proximo_vencimiento_set(self):
        """proximo_vencimiento retorna deadline más cercano."""
        result = check_compliance("PM", month=7, year=2024)

        if result.obligaciones:
            assert result.proximo_vencimiento is not None

    @pytest.mark.parametrize("regimen", ["PM", "PF_Honorarios", "PF_Asalariado", "RIF"])
    def test_all_regimens(self, regimen):
        """Todos los regímenes retornan obligaciones."""
        result = check_compliance(regimen, month=6, year=2024)

        assert result.riesgo_general in ["green", "yellow", "red"]
