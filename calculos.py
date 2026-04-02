"""
REGISTRO DE CÁLCULOS FISCALES DETERMINISTAS
Sonora Digital Corp — HERMES OS

Estas funciones reemplazan al LLM para cálculos exactos.
Cuando HERMES detecta una pregunta calculable → usa esto, no el LLM.
Resultado: respuesta instantánea, 100% exacta, costo $0.

Cómo crece: cuando el LLM responde un cálculo nuevo y el humano lo valida
→ se agrega aquí como función Python → nunca más se paga por esa respuesta.
"""

from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import Optional
import math

# ── Tipos de respuesta ────────────────────────────────────────
@dataclass
class ResultadoFiscal:
    valor: Decimal
    formula: str
    fundamento: str        # artículo de ley, NOM, DOF
    notas: list[str]
    confianza: float = 1.0  # 1.0 = determinista exacto


def _d(x) -> Decimal:
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ════════════════════════════════════════════════════════════
# BLOQUE 1: ISR (Impuesto Sobre la Renta)
# ════════════════════════════════════════════════════════════

# Tabla ISR mensual 2025 (Art. 96 LISR)
_TABLA_ISR_MENSUAL_2025 = [
    (      0.01,    746.04,    0.00,  1.92),
    (    746.05,   6332.05,   14.32,  6.40),
    (   6332.06,  11128.01,  371.83, 10.88),
    (  11128.02,  12935.82,  893.63, 16.00),
    (  12935.83,  15487.71, 1182.88, 17.92),
    (  15487.72,  31236.49, 1640.18, 21.36),
    (  31236.50,  49233.00, 5004.12, 23.52),
    (  49233.01,  93993.90, 9236.89, 30.00),
    (  93993.91, 125325.20,22665.17, 32.00),
    ( 125325.21, 375975.61,32691.18, 34.00),
    ( 375975.62, float('inf'), 117912.32, 35.00),
]

def calcular_isr_mensual(ingreso_mensual: float) -> ResultadoFiscal:
    """
    Calcula ISR mensual para persona física con actividad empresarial.
    Art. 96 LISR 2025.
    """
    ing = _d(ingreso_mensual)
    for li, ls, cuota_fija, tasa in _TABLA_ISR_MENSUAL_2025:
        if _d(li) <= ing <= _d(ls):
            excedente = ing - _d(li)
            tasa_d = _d(tasa) / _d(100)
            isr = _d(cuota_fija) + (excedente * tasa_d)
            return ResultadoFiscal(
                valor=isr,
                formula=f"ISR = ${cuota_fija} + ({ing} - ${li}) × {tasa}%",
                fundamento="Art. 96 LISR, Tabla mensual 2025",
                notas=[f"Tasa marginal: {tasa}%", f"Cuota fija: ${cuota_fija}"],
            )
    raise ValueError(f"Ingreso fuera de tabla: {ingreso_mensual}")


def calcular_isr_anual(ingreso_anual: float, deducciones: float = 0) -> ResultadoFiscal:
    """ISR anual aproximado (declaración anual PF)."""
    base = _d(ingreso_anual) - _d(deducciones)
    resultado_mensual = calcular_isr_mensual(float(base / 12))
    isr_anual = resultado_mensual.valor * 12
    return ResultadoFiscal(
        valor=isr_anual,
        formula=f"ISR anual ≈ ISR mensual ({resultado_mensual.valor}) × 12",
        fundamento="Art. 152 LISR 2025",
        notas=["Cálculo aproximado — usar tabla anual para precisión exacta"],
        confianza=0.92,
    )


# ════════════════════════════════════════════════════════════
# BLOQUE 2: IVA (Impuesto al Valor Agregado)
# ════════════════════════════════════════════════════════════

IVA_TASA_GENERAL = Decimal("0.16")    # 16% zona general
IVA_TASA_FRONTERA = Decimal("0.08")   # 8% zona fronteriza (hasta 2024, verificar DOF)
IVA_TASA_CERO = Decimal("0.00")       # Alimentos, medicamentos


def calcular_iva(subtotal: float, zona: str = "general") -> ResultadoFiscal:
    tasas = {"general": IVA_TASA_GENERAL, "frontera": IVA_TASA_FRONTERA, "cero": IVA_TASA_CERO}
    tasa = tasas.get(zona, IVA_TASA_GENERAL)
    sub = _d(subtotal)
    iva = sub * tasa
    total = sub + iva
    return ResultadoFiscal(
        valor=iva,
        formula=f"IVA = ${subtotal} × {tasa * 100}% = ${iva} | Total: ${total}",
        fundamento="Art. 1° LIVA 2025",
        notas=[f"Zona: {zona}", f"Total con IVA: ${total}"],
    )


def desglosar_iva(total_con_iva: float, zona: str = "general") -> ResultadoFiscal:
    """Extrae IVA de un precio que ya lo incluye."""
    tasas = {"general": IVA_TASA_GENERAL, "frontera": IVA_TASA_FRONTERA}
    tasa = tasas.get(zona, IVA_TASA_GENERAL)
    total = _d(total_con_iva)
    base = total / (1 + tasa)
    iva = total - base
    return ResultadoFiscal(
        valor=iva,
        formula=f"Base = ${total} ÷ (1 + {tasa * 100}%) = ${base:.2f} | IVA = ${iva:.2f}",
        fundamento="Art. 1° LIVA 2025",
        notas=[f"Base gravable: ${base:.2f}", f"IVA incluido: ${iva:.2f}"],
    )


# ════════════════════════════════════════════════════════════
# BLOQUE 3: IMSS / Cuotas de seguridad social
# ════════════════════════════════════════════════════════════

UMA_2025 = Decimal("108.57")   # UMA diaria 2025 (verificar actualizaciones DOF)
SMG_2025 = Decimal("278.80")   # Salario mínimo general 2025

def calcular_cuotas_imss(sbc_diario: float) -> dict:
    """
    Calcula cuotas IMSS por ramas.
    SBC = Salario Base de Cotización diario.
    Art. 25-107 LSS.
    """
    sbc = _d(sbc_diario)
    uma = UMA_2025

    # Enfermedad y Maternidad (EM)
    em_patron  = (sbc - (3 * uma)) * _d("0.0150") if sbc > 3 * uma else _d("0")
    em_obrero  = (sbc - (3 * uma)) * _d("0.00375") if sbc > 3 * uma else _d("0")
    em_patron += sbc * _d("0.00105") + sbc * _d("0.00105")  # prestaciones + gastos médicos

    # Invalidez y Vida
    iv_patron  = sbc * _d("0.01750")
    iv_obrero  = sbc * _d("0.00625")

    # Retiro (solo patrón)
    retiro_patron = sbc * _d("0.02")

    # INFONAVIT (solo patrón)
    infonavit_patron = sbc * _d("0.05")

    # Cesantía y Vejez
    cv_patron = sbc * _d("0.03150")
    cv_obrero = sbc * _d("0.01125")

    total_patron = em_patron + iv_patron + retiro_patron + infonavit_patron + cv_patron
    total_obrero = em_obrero + iv_obrero + cv_obrero

    return {
        "sbc_diario": float(sbc),
        "cuota_patron_diaria": float(total_patron.quantize(_d("0.01"))),
        "cuota_obrero_diaria": float(total_obrero.quantize(_d("0.01"))),
        "cuota_patron_mensual": float((total_patron * 30).quantize(_d("0.01"))),
        "cuota_obrero_mensual": float((total_obrero * 30).quantize(_d("0.01"))),
        "fundamento": "Arts. 25-107 LSS, tablas 2025",
        "nota": "Cálculo aproximado — las ramas tienen límites y topes variables",
    }


# ════════════════════════════════════════════════════════════
# BLOQUE 4: CFDI / Facturación
# ════════════════════════════════════════════════════════════

CFDI_VERSION = "4.0"
CFDI_METODOS_PAGO = {
    "01": "Efectivo", "02": "Cheque nominativo", "03": "Transferencia electrónica",
    "04": "Tarjeta de crédito", "28": "Tarjeta de débito", "99": "Por definir",
}
CFDI_FORMAS_PAGO = {
    "PUE": "Pago en una sola exhibición",
    "PPD": "Pago en parcialidades o diferido",
}
CFDI_USOS = {
    "G01": "Adquisición de mercancias", "G02": "Devoluciones, descuentos o bonificaciones",
    "G03": "Gastos en general", "I01": "Construcciones", "I02": "Mobilario y equipo",
    "I04": "Equipo de cómputo", "I06": "Comunicaciones telefónicas",
    "P01": "Por definir", "S01": "Sin efectos fiscales",
    "D01": "Honorarios médicos", "D03": "Gastos funerales",
    "CN01": "Nómina", "CP01": "Pagos",
}

def validar_cfdi_totales(subtotal: float, descuento: float = 0,
                          iva_trasladado: float = 0, isr_retenido: float = 0,
                          iva_retenido: float = 0) -> dict:
    """Valida que los totales de un CFDI cuadren correctamente."""
    sub = _d(subtotal)
    desc = _d(descuento)
    iva = _d(iva_trasladado)
    isr_ret = _d(isr_retenido)
    iva_ret = _d(iva_retenido)

    total = sub - desc + iva - isr_ret - iva_ret
    base_gravable = sub - desc

    return {
        "subtotal": float(sub),
        "descuento": float(desc),
        "base_gravable": float(base_gravable),
        "iva_16%": float(base_gravable * _d("0.16")),
        "iva_declarado": float(iva),
        "isr_retenido": float(isr_ret),
        "iva_retenido": float(iva_ret),
        "total_calculado": float(total),
        "cuadra": abs(float(total) - float(sub - desc + iva - isr_ret - iva_ret)) < 0.01,
        "version": CFDI_VERSION,
    }


# ════════════════════════════════════════════════════════════
# BLOQUE 5: ADUANAS / Importación
# ════════════════════════════════════════════════════════════

def calcular_contribuciones_importacion(
    valor_aduana_usd: float,
    tipo_cambio: float,
    arancel_pct: float,
    incluye_iva: bool = True,
    incluye_dta: bool = True,
) -> dict:
    """
    Calcula contribuciones de importación (base).
    Valor en aduana: método de valor de transacción (Art. 64 LA).
    """
    va_mxn = _d(valor_aduana_usd) * _d(tipo_cambio)
    arancel = va_mxn * (_d(arancel_pct) / 100)
    base_iva = va_mxn + arancel

    iva = base_iva * _d("0.16") if incluye_iva else _d("0")

    # DTA: Derecho de Trámite Aduanero (8/1000 del valor aduana, mín $569, máx no aplica normal)
    dta = max(va_mxn * _d("0.008"), _d("569.00")) if incluye_dta else _d("0")

    total = va_mxn + arancel + iva + dta

    return {
        "valor_aduana_usd": valor_aduana_usd,
        "tipo_cambio": tipo_cambio,
        "valor_aduana_mxn": float(va_mxn),
        "arancel": float(arancel),
        "base_iva": float(base_iva),
        "iva_16pct": float(iva),
        "dta": float(dta),
        "total_contribuciones": float(total),
        "costo_total_mxn": float(total),
        "fundamento": "Arts. 64, 65 LA | Art. 49 LFD (DTA) | LIVA",
    }


def calcular_manifestacion_valor(
    precio_pagado_usd: float,
    flete_usd: float,
    seguro_usd: float,
    tipo_cambio: float,
    otros_gastos_usd: float = 0,
) -> dict:
    """
    Calcula Manifestación de Valor (Método de Valor de Transacción).
    Art. 64-78 Ley Aduanera. Obligatorio para importaciones > $1,000 USD.
    """
    precio = _d(precio_pagado_usd)
    flete  = _d(flete_usd)
    seguro = _d(seguro_usd)
    otros  = _d(otros_gastos_usd)
    tc     = _d(tipo_cambio)

    valor_transaccion = precio + flete + seguro + otros
    valor_aduana_mxn  = valor_transaccion * tc

    return {
        "precio_pagado_usd": float(precio),
        "flete_usd":         float(flete),
        "seguro_usd":        float(seguro),
        "otros_gastos_usd":  float(otros),
        "valor_transaccion_usd": float(valor_transaccion),
        "tipo_cambio": float(tc),
        "valor_aduana_mxn": float(valor_aduana_mxn),
        "metodo": "Valor de Transacción (Método 1)",
        "fundamento": "Art. 64 Ley Aduanera | Art. 1° Acuerdo de Valoración OMC",
        "requiere_manifestacion": float(precio) >= 1000,
        "nota": "Presentar e-document Manifestación de Valor al importar",
    }


# ════════════════════════════════════════════════════════════
# BLOQUE 6: DECLARACIONES / Plazos
# ════════════════════════════════════════════════════════════

from datetime import date

OBLIGACIONES_CALENDARIO = {
    "diot_mensual":          {"dia": 17, "descripcion": "DIOT — Declaración de Operaciones con Terceros"},
    "pago_provisional_pm":   {"dia": 17, "descripcion": "Pago provisional ISR/IVA PM"},
    "pago_provisional_pf":   {"dia": 17, "descripcion": "Pago provisional ISR/IVA PF"},
    "cfdi_nomina_bimestral": {"dia": 17, "descripcion": "CFDI nómina RIF (bimestral)"},
    "declaracion_anual_pm":  {"mes": 3,  "dia": 31, "descripcion": "Declaración anual PM (marzo)"},
    "declaracion_anual_pf":  {"mes": 4,  "dia": 30, "descripcion": "Declaración anual PF (abril)"},
}

def dias_para_declaracion(tipo: str, hoy: date = None) -> dict:
    """Calcula días restantes para una obligación fiscal."""
    if hoy is None:
        hoy = date.today()
    oblig = OBLIGACIONES_CALENDARIO.get(tipo)
    if not oblig:
        return {"error": f"Obligación '{tipo}' no registrada"}

    mes_vence = oblig.get("mes", hoy.month if hoy.day <= oblig["dia"] else hoy.month + 1)
    if mes_vence > 12:
        mes_vence = 1
        año_vence = hoy.year + 1
    else:
        año_vence = hoy.year

    try:
        vencimiento = date(año_vence, mes_vence, oblig["dia"])
        if vencimiento < hoy:
            mes_vence = mes_vence + 1 if mes_vence < 12 else 1
            año_vence = año_vence if mes_vence > 1 else año_vence + 1
            vencimiento = date(año_vence, mes_vence, oblig["dia"])

        dias = (vencimiento - hoy).days
        return {
            "obligacion": oblig["descripcion"],
            "vencimiento": str(vencimiento),
            "dias_restantes": dias,
            "urgente": dias <= 5,
            "atrasado": dias < 0,
        }
    except Exception as e:
        return {"error": str(e)}


# ════════════════════════════════════════════════════════════
# REGISTRO: detección automática de tipo de pregunta
# ════════════════════════════════════════════════════════════

PATRON_CALCULOS = {
    "isr_mensual":       ["isr", "impuesto sobre la renta", "cuánto pago de isr", "isr mensual"],
    "iva":               ["iva", "impuesto al valor agregado", "cuánto es el iva", "calcular iva"],
    "imss":              ["imss", "cuotas imss", "seguridad social", "sbc"],
    "cfdi":              ["cfdi", "factura", "comprobante fiscal", "timbrar"],
    "importacion":       ["importación", "aduanas", "pedimento", "contribuciones importación"],
    "manifestacion":     ["manifestación de valor", "valor de transacción", "valor aduana"],
    "declaracion":       ["declaración", "plazo", "vencimiento", "cuándo debo presentar"],
}

def detectar_calculo(pregunta: str) -> Optional[str]:
    """Detecta si la pregunta es un cálculo determinista."""
    p = pregunta.lower()
    for tipo, keywords in PATRON_CALCULOS.items():
        if any(k in p for k in keywords):
            return tipo
    return None
