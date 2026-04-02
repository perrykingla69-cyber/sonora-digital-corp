"""
Cálculos fiscales México 2026 — tablas oficiales SAT
"""
from typing import Dict

# ── IVA ──────────────────────────────────────────────────────────────────────
def calcular_iva(subtotal: float, tasa: float = 0.16) -> float:
    return round(subtotal * tasa, 2)

# ── IEPS ─────────────────────────────────────────────────────────────────────
def calcular_ieps(subtotal: float, tipo: str = "otro") -> float:
    tasas = {"combustible": 0.1645, "cerveza": 0.26, "tabaco": 0.160, "otro": 0.0}
    return round(subtotal * tasas.get(tipo, 0.0), 2)

# ── ISR mensual tabla SAT 2026 (Art. 96 LISR) ────────────────────────────────
# Límite inferior, límite superior, cuota fija, porcentaje sobre excedente
_TABLA_ISR_MENSUAL_2026 = [
    (0.01,       746.04,    0.00,     1.92),
    (746.05,     6_332.05,  14.32,    6.40),
    (6_332.06,   11_128.01, 371.83,   10.88),
    (11_128.02,  12_935.82, 893.63,   16.00),
    (12_935.83,  15_487.71, 1_182.88, 17.92),
    (15_487.72,  31_236.49, 1_640.18, 21.36),
    (31_236.50,  49_233.00, 5_004.12, 23.52),
    (49_233.01,  93_993.90, 9_236.89, 30.00),
    (93_993.91,  125_325.20, 22_665.17, 32.00),
    (125_325.21, 375_975.61, 32_691.18, 34.00),
    (375_975.62, float('inf'), 117_912.32, 35.00),
]

def calcular_isr(base: float, tasa: float = 0.30) -> float:
    """ISR rápido con tasa fija — usar calcular_isr_tabla para nómina."""
    return round(base * tasa, 2)

def calcular_isr_tabla(ingreso_mensual: float) -> Dict[str, float]:
    """
    ISR mensual con tabla oficial SAT 2026.
    Retorna: isr_causado, subsidio_empleo, isr_retenido
    """
    isr = 0.0
    for li, ls, cuota, pct in _TABLA_ISR_MENSUAL_2026:
        if li <= ingreso_mensual <= ls:
            excedente = ingreso_mensual - li
            isr = round(cuota + (excedente * pct / 100), 2)
            break

    # Subsidio al empleo 2026 (tabla simplificada)
    subsidio = _subsidio_empleo(ingreso_mensual)
    isr_retenido = max(0.0, round(isr - subsidio, 2))

    return {
        "isr_causado": isr,
        "subsidio_empleo": subsidio,
        "isr_retenido": isr_retenido,
    }

# ── Subsidio al empleo 2026 ───────────────────────────────────────────────────
_TABLA_SUBSIDIO = [
    (0.01,     1_768.96, 407.02),
    (1_768.97, 1_978.70, 406.83),
    (1_978.71, 2_653.38, 406.62),
    (2_653.39, 3_472.84, 392.77),
    (3_472.85, 3_537.87, 347.63),
    (3_537.88, 4_446.15, 347.63),
    (4_446.16, 4_717.18, 338.42),
    (4_717.19, 5_335.42, 242.84),
    (5_335.43, 6_224.67, 162.61),
    (6_224.68, 7_113.90, 81.32),
    (7_113.91, float('inf'), 0.00),
]

def _subsidio_empleo(salario: float) -> float:
    for li, ls, subsidio in _TABLA_SUBSIDIO:
        if li <= salario <= ls:
            return subsidio
    return 0.0

# ── UMA 2026 ──────────────────────────────────────────────────────────────────
UMA_DIARIA_2026  = 108.57
UMA_MENSUAL_2026 = 3_300.53
UMA_ANUAL_2026   = 39_606.36

# ── IMSS trabajador 2026 ──────────────────────────────────────────────────────
def calcular_imss_trabajador(salario_diario: float, dias: int = 30) -> Dict[str, float]:
    sdi = salario_diario  # Salario Diario Integrado
    uma = UMA_DIARIA_2026

    # Enfermedad y maternidad
    excedente_3uma = max(0, sdi - uma * 3)
    enf_mat_cuota  = round(uma * 3 * 0.0040 * dias, 2)
    enf_mat_exc    = round(excedente_3uma * 0.004 * dias, 2)
    invalidez_vida = round(sdi * 0.00625 * dias, 2)
    cesantia_vejez = round(sdi * 0.01125 * dias, 2)

    total = round(enf_mat_cuota + enf_mat_exc + invalidez_vida + cesantia_vejez, 2)
    return {
        "enf_mat_cuota_fija": enf_mat_cuota,
        "enf_mat_excedente":  enf_mat_exc,
        "invalidez_vida":     invalidez_vida,
        "cesantia_vejez":     cesantia_vejez,
        "total_imss":         total,
    }
