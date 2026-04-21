import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from operations.validate_cfdi import validate_cfdi


class TestValidateCFDI:
    """Tests para validación CFDI 4.0."""

    def test_cfdi_valid(self, sample_cfdi_valid):
        """CFDI válido pasa validación."""
        result = validate_cfdi(json_content=sample_cfdi_valid)

        assert result.valid is True
        assert len(result.errors) == 0
        assert result.version == "4.0"

    def test_cfdi_invalid_rfc(self, sample_cfdi_invalid):
        """CFDI con RFC inválido falla."""
        result = validate_cfdi(json_content=sample_cfdi_invalid)

        assert result.valid is False
        assert len(result.errors) > 0
        assert any('RFC' in e.field for e in result.errors)

    def test_cfdi_invalid_iva_rate(self):
        """CFDI con tasa IVA inválida (21%) falla."""
        cfdi = {
            "RFC_Emisor": "AAA010101AAA",
            "RFC_Receptor": "XIA190128TA7",
            "Montos": {"Subtotal": 1000, "IVA": 210, "Total": 1210},
            "Conceptos": [
                {"Descripcion": "Servicio", "Monto": 1000, "TasaIVA": 0.21}
            ]
        }
        result = validate_cfdi(json_content=cfdi)

        assert result.valid is False
        assert any('TasaIVA' in e.field for e in result.errors)

    def test_cfdi_negative_amount(self):
        """CFDI con montos negativos falla."""
        cfdi = {
            "RFC_Emisor": "AAA010101AAA",
            "RFC_Receptor": "XIA190128TA7",
            "Montos": {"Subtotal": -1000, "IVA": -160, "Total": -1160},
            "Conceptos": []
        }
        result = validate_cfdi(json_content=cfdi)

        assert result.valid is False
        assert len(result.errors) > 0

    def test_cfdi_empty(self):
        """CFDI vacío retorna error."""
        result = validate_cfdi(json_content=None)

        assert result.valid is False
        assert len(result.errors) > 0

    @pytest.mark.parametrize("rfc_valid", [
        "AAA010101AAA",
        "XIA190128TA7",
        "ABCD971102AAA",
    ])
    def test_rfc_valid_formats(self, rfc_valid):
        """RFCs válidos pasan."""
        cfdi = {
            "RFC_Emisor": rfc_valid,
            "RFC_Receptor": "XIA190128TA7",
            "Montos": {"Subtotal": 1000},
            "Conceptos": []
        }
        result = validate_cfdi(json_content=cfdi)

        # No debe haber error de RFC_Emisor
        assert not any(e.field == "RFC_Emisor" for e in result.errors)
