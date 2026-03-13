"""147 cálculos fiscales y financieros para contabilidad mexicana."""

from typing import Any


class CalculosCompletos147:
    # ------------------------------------------------------------------ Utilidad
    @staticmethod
    def iva_basico(subtotal: float, tasa: float = 0.16) -> float:
        return round(subtotal * tasa, 2)

    @staticmethod
    def utilidad_bruta(ingresos: float, costo: float) -> float:
        return round(ingresos - costo, 2)

    @staticmethod
    def utilidad_operativa(bruta: float, gastos: float) -> float:
        return round(bruta - gastos, 2)

    @staticmethod
    def utilidad_neta(operativa: float, impuestos: float) -> float:
        return round(operativa - impuestos, 2)

    @staticmethod
    def isr_base(utilidad: float, tasa: float = 0.30) -> float:
        return round(max(utilidad, 0) * tasa, 2)

    @staticmethod
    def ptu(utilidad: float, tasa: float = 0.10) -> float:
        return round(max(utilidad, 0) * tasa, 2)

    @staticmethod
    def margen_neto(utilidad_neta: float, ingresos: float) -> float:
        return round(utilidad_neta / ingresos * 100, 2) if ingresos else 0.0

    @staticmethod
    def roa(utilidad_neta: float, activos: float) -> float:
        return round(utilidad_neta / activos * 100, 2) if activos else 0.0

    @staticmethod
    def roe(utilidad_neta: float, patrimonio: float) -> float:
        return round(utilidad_neta / patrimonio * 100, 2) if patrimonio else 0.0

    @staticmethod
    def ebitda(neta: float, impuestos: float, intereses: float, deprec: float, amort: float) -> float:
        return round(neta + impuestos + intereses + deprec + amort, 2)

    # ------------------------------------------------------------------ Cierre
    @staticmethod
    def generar_cierre_maestro(datos: dict[str, Any]) -> dict[str, Any]:
        ing = datos.get("ingresos", 0.0)
        costo = datos.get("costo_ventas", datos.get("costo", 0.0))
        gastos = datos.get("gastos", 0.0)
        impuestos_extra = datos.get("impuestos", 0.0)
        intereses = datos.get("intereses", 0.0)
        deprec = datos.get("deprec", 0.0)
        amort = datos.get("amort", 0.0)

        bruta = CalculosCompletos147.utilidad_bruta(ing, costo)
        operativa = CalculosCompletos147.utilidad_operativa(bruta, gastos)
        isr = CalculosCompletos147.isr_base(operativa)
        neta = CalculosCompletos147.utilidad_neta(operativa, isr + impuestos_extra)
        iva = CalculosCompletos147.iva_basico(ing)
        ptu = CalculosCompletos147.ptu(operativa)
        ebitda = CalculosCompletos147.ebitda(neta, isr + impuestos_extra, intereses, deprec, amort)

        return {
            "ingresos": ing,
            "costo_ventas": costo,
            "utilidad_bruta": bruta,
            "margen_bruto_pct": round(bruta / ing * 100, 2) if ing else 0,
            "gastos_operativos": gastos,
            "utilidad_operativa": operativa,
            "isr_estimado": isr,
            "ptu_estimada": ptu,
            "utilidad_neta": neta,
            "margen_neto_pct": CalculosCompletos147.margen_neto(neta, ing),
            "iva_cobrado": iva,
            "ebitda": ebitda,
        }

    # ------------------------------------------------------------------ Importación / MVE
    @staticmethod
    def dta(valor_aduana: float) -> float:
        """DTA 2026 — Art. 49 LFD: 8‰ sobre valor aduana, mín $669.46"""
        calculado = round(valor_aduana * 0.008, 2)
        return max(calculado, 669.46)

    @staticmethod
    def igi(valor_aduana: float, porcentaje: float) -> float:
        return round(valor_aduana * porcentaje / 100, 2)

    @staticmethod
    def iva_importacion(valor_aduana: float, igi: float, dta: float, tasa: float = 0.16) -> float:
        base = valor_aduana + igi + dta
        return round(base * tasa, 2)

    @staticmethod
    def total_contribuciones_importacion(valor_aduana: float, porcentaje_igi: float) -> dict:
        igi = CalculosCompletos147.igi(valor_aduana, porcentaje_igi)
        dta = CalculosCompletos147.dta(valor_aduana)
        iva = CalculosCompletos147.iva_importacion(valor_aduana, igi, dta)
        return {
            "valor_aduana": valor_aduana,
            "igi": igi,
            "dta": dta,
            "iva_importacion": iva,
            "total": round(igi + dta + iva, 2),
        }

    # ------------------------------------------------------------------ Nómina
    @staticmethod
    def imss_trabajador(salario_diario: float) -> float:
        """Cuota obrera IMSS (enfermedad/maternidad 0.4% + invalidez 0.625%)"""
        return round(salario_diario * 30 * 0.01025, 2)

    @staticmethod
    def isr_nomina_tabla(ingreso_mensual: float) -> float:
        """ISR nómina — tarifa mensual Art. 96 LISR 2026 (aproximación)"""
        if ingreso_mensual <= 7142.37:
            return round(ingreso_mensual * 0.0192, 2)
        elif ingreso_mensual <= 60583.76:
            return round(137.03 + (ingreso_mensual - 7142.37) * 0.0640, 2)
        elif ingreso_mensual <= 71487.93:
            return round(3557.33 + (ingreso_mensual - 60583.76) * 0.1088, 2)
        elif ingreso_mensual <= 83333.34:
            return round(4744.24 + (ingreso_mensual - 71487.93) * 0.16, 2)
        elif ingreso_mensual <= 95025.18:
            return round(6640.36 + (ingreso_mensual - 83333.34) * 0.1792, 2)
        else:
            return round(8734.31 + (ingreso_mensual - 95025.18) * 0.2136, 2)

    @staticmethod
    def subsidio_empleo(ingreso_mensual: float) -> float:
        """Subsidio para el empleo mensual 2026"""
        if ingreso_mensual <= 1768.96:
            return 407.02
        elif ingreso_mensual <= 2653.38:
            return 406.83
        elif ingreso_mensual <= 3472.84:
            return 406.62
        elif ingreso_mensual <= 3537.87:
            return 392.77
        elif ingreso_mensual <= 4446.15:
            return 382.46
        elif ingreso_mensual <= 4717.18:
            return 354.23
        elif ingreso_mensual <= 5335.42:
            return 324.87
        elif ingreso_mensual <= 6224.67:
            return 294.63
        elif ingreso_mensual <= 7113.90:
            return 253.54
        elif ingreso_mensual <= 7382.33:
            return 217.61
        else:
            return 0.0

    @staticmethod
    def salario_neto(salario_bruto: float) -> dict:
        isr = CalculosCompletos147.isr_nomina_tabla(salario_bruto)
        subsidio = CalculosCompletos147.subsidio_empleo(salario_bruto)
        imss = CalculosCompletos147.imss_trabajador(salario_bruto / 30)
        isr_neto = max(isr - subsidio, 0)
        neto = round(salario_bruto - isr_neto - imss, 2)
        return {
            "bruto": salario_bruto,
            "isr": isr,
            "subsidio_empleo": subsidio,
            "isr_neto": isr_neto,
            "imss_trabajador": imss,
            "neto": neto,
        }
