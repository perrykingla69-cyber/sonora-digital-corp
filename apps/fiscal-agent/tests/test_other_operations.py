import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from operations.alert_deadline import alert_deadline
from operations.validate_receipt import validate_receipt
from operations.get_tax_catalogs import get_tax_catalogs
from operations.generate_compliance_report import generate_compliance_report


class TestAlertDeadline:
    """Tests para cálculo deadlines."""

    def test_alert_deadline_default_month(self):
        """Alert deadline para obligación actual."""
        result = alert_deadline("ISR_Mensual")

        assert result.obligacion == "ISR_Mensual"
        assert result.deadline
        assert result.alerta_fecha
        assert isinstance(result.dias_restantes, int)

    def test_alert_deadline_specific_month(self):
        """Alert deadline para mes específico."""
        result = alert_deadline("ISR_Mensual", month=7, year=2024)

        assert result.deadline
        # ISR mes 7 vence 17-julio
        assert "2024-07" in result.deadline

    def test_alert_deadline_fields(self):
        """Todos los campos requeridos presentes."""
        result = alert_deadline("IMSS", month=6, year=2024)

        assert hasattr(result, 'obligacion')
        assert hasattr(result, 'deadline')
        assert hasattr(result, 'alerta_fecha')
        assert hasattr(result, 'dias_restantes')


class TestValidateReceipt:
    """Tests para validación recibos."""

    def test_receipt_valid_with_rfc(self):
        """Recibo con RFC válido es deductible."""
        result = validate_receipt(
            tipo="factura",
            monto=1000.0,
            rfc_emisor="AAA010101AAA"
        )

        assert result.deductible is True
        assert len(result.requisitos) > 0

    def test_receipt_invalid_no_rfc(self):
        """Recibo sin RFC no es deductible."""
        result = validate_receipt(
            tipo="recibo",
            monto=500.0,
            rfc_emisor=None
        )

        assert result.deductible is False

    def test_receipt_invalid_rfc_format(self):
        """RFC inválido genera advertencia."""
        result = validate_receipt(
            tipo="factura",
            monto=1000.0,
            rfc_emisor="INVALIDO"
        )

        assert result.deductible is False
        assert len(result.advertencias) > 0

    def test_receipt_negative_amount(self):
        """Monto negativo no deductible."""
        result = validate_receipt(
            tipo="factura",
            monto=-100.0,
            rfc_emisor="AAA010101AAA"
        )

        assert result.deductible is False

    def test_receipt_fields(self):
        """Response contiene campos requeridos."""
        result = validate_receipt("factura", 500.0, "AAA010101AAA")

        assert hasattr(result, 'deductible')
        assert hasattr(result, 'requisitos')
        assert hasattr(result, 'advertencias')


class TestGetTaxCatalogs:
    """Tests para catálogos SAT."""

    def test_catalog_tabla18(self):
        """Catálogo tabla18 retorna tipos comprobante."""
        result = get_tax_catalogs("tabla18")

        assert result.items
        assert len(result.items) > 0
        assert result.source

    def test_catalog_tasas_iva(self):
        """Catálogo tasas_iva retorna tasas válidas."""
        result = get_tax_catalogs("tasas_iva")

        assert result.items
        assert len(result.items) == 3  # 0%, 8%, 16%
        for item in result.items:
            assert item.valor in [0.0, 0.08, 0.16]

    def test_catalog_tasas_isr(self):
        """Catálogo tasas_isr retorna tabla progresiva."""
        result = get_tax_catalogs("tasas_isr")

        assert result.items
        assert len(result.items) > 0
        # Todos los items deben tener valor (tarifa)
        assert all(item.valor is not None for item in result.items)

    def test_catalog_response_format(self):
        """Response contiene campos requeridos."""
        result = get_tax_catalogs("tabla18")

        assert hasattr(result, 'items')
        assert hasattr(result, 'updated')
        assert hasattr(result, 'source')


class TestComplianceReport:
    """Tests para reportes cumplimiento."""

    def test_compliance_report_pm(self):
        """Reporte cumplimiento PM."""
        result = generate_compliance_report("202406", "PM")

        assert result.periodo == "202406"
        assert result.regimen == "PM"
        assert result.resumen
        assert result.riesgo in ["green", "yellow", "red"]

    def test_compliance_report_pf_honorarios(self):
        """Reporte cumplimiento PF Honorarios."""
        result = generate_compliance_report("202407", "PF_Honorarios")

        assert result.obligaciones_cumplidas or result.obligaciones_pendientes
        assert hasattr(result, 'riesgo')

    def test_compliance_report_fields(self):
        """Todos campos requeridos presentes."""
        result = generate_compliance_report("202405", "RIF")

        assert hasattr(result, 'periodo')
        assert hasattr(result, 'regimen')
        assert hasattr(result, 'resumen')
        assert hasattr(result, 'obligaciones_cumplidas')
        assert hasattr(result, 'obligaciones_pendientes')
        assert hasattr(result, 'riesgo')

    @pytest.mark.parametrize("regimen", ["PM", "PF_Honorarios", "RIF", "PF_Asalariado"])
    def test_report_all_regimens(self, regimen):
        """Todos regímenes generan reporte."""
        result = generate_compliance_report("202406", regimen)

        assert result.regimen == regimen
        assert result.riesgo in ["green", "yellow", "red"]
