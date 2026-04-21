import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_pyme():
    """PYME típica: $150k ingresos, $50k gastos."""
    return {
        "ingresos": 150000,
        "gastos": 50000,
        "periodo": "202406",
        "regimen": "PM"
    }


@pytest.fixture
def sample_freelancer():
    """Freelancer honorarios: $80k ingresos, $20k gastos."""
    return {
        "ingresos": 80000,
        "gastos": 20000,
        "periodo": "202406",
        "regimen": "PF_Honorarios"
    }


@pytest.fixture
def sample_cfdi_valid():
    """CFDI válido JSON."""
    return {
        "RFC_Emisor": "AAA010101AAA",
        "RFC_Receptor": "XIA190128TA7",
        "Montos": {"Subtotal": 1000, "IVA": 160, "Total": 1160},
        "Conceptos": [
            {"Descripcion": "Servicio", "Monto": 1000, "TasaIVA": 0.16}
        ]
    }


@pytest.fixture
def sample_cfdi_invalid():
    """CFDI inválido: RFC mal."""
    return {
        "RFC_Emisor": "ABC",  # Inválido
        "RFC_Receptor": "XIA190128TA7",
        "Montos": {"Subtotal": 1000, "IVA": 160, "Total": 1160},
        "Conceptos": [
            {"Descripcion": "Servicio", "Monto": 1000, "TasaIVA": 0.21}  # Tasa IVA inválida
        ]
    }
