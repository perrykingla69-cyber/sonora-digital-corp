from datetime import datetime
from schemas.fiscal_responses import TaxCatalogResult, TaxCatalogItem
from rules import tax_rules_2024 as tax_rules


def get_tax_catalogs(query: str, period: str = None) -> TaxCatalogResult:
    """Retorna catálogos SAT por query."""

    items = []

    if query == "tabla18":
        # Tipos comprobante SAT
        items = [
            TaxCatalogItem(codigo="01", descripcion="Factura"),
            TaxCatalogItem(codigo="02", descripcion="Factura simplificada"),
            TaxCatalogItem(codigo="03", descripcion="Recibo"),
            TaxCatalogItem(codigo="04", descripcion="Retención"),
            TaxCatalogItem(codigo="05", descripcion="Traslado"),
        ]

    elif query == "tasas_iva":
        items = [
            TaxCatalogItem(codigo="0", descripcion="Tasa 0%", valor=0.0),
            TaxCatalogItem(codigo="8", descripcion="Tasa 8%", valor=0.08),
            TaxCatalogItem(codigo="16", descripcion="Tasa 16%", valor=0.16),
        ]

    elif query == "tasas_isr":
        # Tabla progresiva resumida
        tablas = tax_rules.TAX_TABLES['isr']['tablas_progresivas']['2024']
        for i, tramo in enumerate(tablas):
            if 'tarifa' in tramo:
                items.append(TaxCatalogItem(
                    codigo=f"tramo_{i+1}",
                    descripcion=f"Desde {tramo['desde']:,.2f} - Tarifa {tramo['tarifa']*100:.1f}%",
                    valor=tramo['tarifa']
                ))

    return TaxCatalogResult(
        items=items,
        updated=datetime.now().isoformat(),
        source="DOF - SAT 2024"
    )
