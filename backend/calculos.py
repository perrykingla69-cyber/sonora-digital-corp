"""Cálculos fiscales básicos — usados por los routers."""

# IVA
def calcular_iva(subtotal: float, tasa: float = 0.16) -> float:
    return round(subtotal * tasa, 2)

# ISR
def calcular_isr(base: float, tasa: float = 0.30) -> float:
    return round(base * tasa, 2)

# IEPS
def calcular_ieps(subtotal: float, tipo: str = "otro") -> float:
    tasas = {"combustible": 0.1645, "cerveza": 0.26, "otro": 0.0}
    return round(subtotal * tasas.get(tipo, 0.0), 2)
