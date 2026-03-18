"""
Motor de validación MVE anti-multa
RGCE 2025 / Ley Aduanera Art. 59-A
Vigente: 1 de abril de 2026
"""
import re
from typing import Optional


# ── Constantes legales ────────────────────────────────────────────────────────

INCOTERMS_VALIDOS = {"EXW","FCA","CPT","CIP","DAP","DPU","DDP","FAS","FOB","CFR","CIF"}
METODOS_VALORACION = {
    1: "Valor de transacción (Art. 45 LA)",
    2: "Valor de transacción de mercancías idénticas (Art. 46 LA)",
    3: "Valor de transacción de mercancías similares (Art. 47 LA)",
    4: "Valor deductivo (Art. 48 LA)",
    5: "Valor reconstruido (Art. 49 LA)",
    6: "Último recurso (Art. 50 LA)",
}
# Incoterms donde es obligatorio declarar flete/seguro
INCOTERMS_REQUIEREN_AJUSTE = {"EXW", "FCA", "FAS", "FOB"}
# Regex pedimento: AA/AAAA/NNNNNN o NNNNNN o formato SAT con espacios
REGEX_PEDIMENTO = re.compile(r"^\d{2}/\d{4}/\d{6,7}$|^\d{6,7}$|^\d{2}\s\d{2}\s\d{4}\s\d{7}$")
REGEX_FRACCION  = re.compile(r"^\d{4}\.\d{2}\.\d{2}\.\d{2}$|^\d{8}$|^\d{10}$")


def validar_mve(mve) -> dict:
    """
    Valida un objeto MVE contra RGCE y devuelve:
    {
        semaforo: 'red' | 'yellow' | 'green',
        errores: [{nivel, codigo, mensaje, campo}],
        puede_presentar: bool,
        resumen: str,
        total_errores: int,
        total_advertencias: int,
    }
    """
    errores = []

    def error(nivel, codigo, mensaje, campo=None):
        errores.append({"nivel": nivel, "codigo": codigo, "mensaje": mensaje, "campo": campo})

    # ── ROJOS — bloqueantes ──────────────────────────────────────────────────

    # MVE-001/002: Pedimento
    pedimento = getattr(mve, "pedimento_numero", None) or ""
    if not pedimento.strip():
        error("red", "MVE-001", "Número de pedimento es obligatorio", "pedimento_numero")
    elif not REGEX_PEDIMENTO.match(pedimento.strip()):
        error("red", "MVE-002",
              f"Formato de pedimento inválido: '{pedimento}'. "
              f"Formato correcto: AA/AAAA/NNNNNN (ej: 04/2026/123456)", "pedimento_numero")

    # MVE-003: Valor factura
    valor = getattr(mve, "valor_factura", 0) or 0
    if valor <= 0:
        error("red", "MVE-003", "Valor de la factura debe ser mayor a cero", "valor_factura")

    # MVE-004/005: Fracción arancelaria
    fraccion = getattr(mve, "fraccion_arancelaria", None) or ""
    if not fraccion.strip():
        error("red", "MVE-004", "Fracción arancelaria es obligatoria", "fraccion_arancelaria")
    elif not REGEX_FRACCION.match(fraccion.replace(".", "").strip()):
        error("red", "MVE-005",
              f"Formato de fracción arancelaria inválido: '{fraccion}'. "
              f"Formato correcto: DDDD.DD.DD.XX", "fraccion_arancelaria")

    # MVE-006/007: Método valoración
    metodo = getattr(mve, "metodo_valoracion", None)
    if metodo is None:
        error("red", "MVE-006",
              "Método de valoración es obligatorio (Art. 45-50 Ley Aduanera). "
              "El 95% de las operaciones usa Método 1 (valor de transacción)", "metodo_valoracion")
    elif metodo not in METODOS_VALORACION:
        error("red", "MVE-007",
              f"Método de valoración '{metodo}' no válido. Debe ser 1-6", "metodo_valoracion")

    # MVE-008: Método 1 requiere valor > 0 (ya validado en MVE-003)

    # MVE-009/010: INCOTERM
    incoterm = getattr(mve, "incoterm", None) or ""
    if not incoterm.strip():
        error("red", "MVE-009",
              "INCOTERM es obligatorio. Indica las condiciones de entrega pactadas "
              "con el proveedor (ej: FOB, CIF, EXW)", "incoterm")
    elif incoterm.upper() not in INCOTERMS_VALIDOS:
        error("red", "MVE-010",
              f"INCOTERM '{incoterm}' no reconocido. "
              f"Válidos: {', '.join(sorted(INCOTERMS_VALIDOS))}", "incoterm")

    # MVE-011: País de origen (proveedor_pais)
    pais_origen = getattr(mve, "proveedor_pais", None) or ""
    if not pais_origen.strip():
        error("red", "MVE-011",
              "País de origen/procedencia de la mercancía es obligatorio "
              "(afecta preferencias arancelarias T-MEC, etc.)", "proveedor_pais")

    # MVE-012: Descripción suficiente
    descripcion = getattr(mve, "descripcion_mercancias", None) or ""
    if len(descripcion.strip()) < 10:
        error("red", "MVE-012",
              "Descripción de la mercancía muy corta. Debe ser suficientemente "
              "específica para clasificación arancelaria correcta (mín. 10 caracteres)", "descripcion_mercancias")

    # MVE-013: Tipo de cambio
    tc = getattr(mve, "tipo_cambio", 0) or 0
    if tc <= 0:
        error("red", "MVE-013",
              "Tipo de cambio es obligatorio y debe ser mayor a cero", "tipo_cambio")

    # ── AMARILLOS — advertencias ─────────────────────────────────────────────

    hay_vinculacion = getattr(mve, "hay_vinculacion", False)
    if hay_vinculacion:
        justificacion_vinc = getattr(mve, "justificacion_vinculacion", None) or ""
        if not justificacion_vinc.strip():
            error("yellow", "MVE-W001",
                  "Declaraste vinculación entre comprador y vendedor. Debes justificar "
                  "que la vinculación NO influyó en el precio, o indicar el método "
                  "alternativo de valoración (Art. 64-A Ley Aduanera)", "justificacion_vinculacion")

    if incoterm and incoterm.upper() in INCOTERMS_REQUIEREN_AJUSTE:
        flete = getattr(mve, "flete", 0) or 0
        seguro = getattr(mve, "seguro", 0) or 0
        if flete == 0 and seguro == 0:
            error("yellow", "MVE-W003",
                  f"Con INCOTERM {incoterm.upper()} el precio NO incluye flete ni seguro. "
                  f"Debes declarar flete y seguro como ajustes incrementables (Art. 65 LA) "
                  f"o justificar que son cero",
                  "flete")

    if metodo and metodo > 1:
        justificacion_metodo = getattr(mve, "justificacion_metodo", None) or ""
        if not justificacion_metodo.strip():
            error("yellow", "MVE-W004",
                  f"Usas Método {metodo} ({METODOS_VALORACION.get(metodo, '')}). "
                  f"Los métodos 2-6 requieren justificación escrita de por qué no aplica el Método 1. "
                  f"Sin esta justificación, la aduana puede rechazar o multar", "justificacion_metodo")

    tasa_igi = getattr(mve, "tasa_igi", 0) or 0
    if tasa_igi == 0 and fraccion.strip():
        error("yellow", "MVE-W005",
              f"IGI = 0%. Confirma que la fracción {fraccion} tiene tasa 0% "
              f"o que aplica preferencia arancelaria (T-MEC, etc.) y tienes certificado de origen",
              "tasa_igi")

    # ── Semáforo final ───────────────────────────────────────────────────────
    rojos     = [e for e in errores if e["nivel"] == "red"]
    amarillos = [e for e in errores if e["nivel"] == "yellow"]

    if rojos:
        semaforo = "red"
        puede_presentar = False
        resumen = (f"🔴 NO PUEDE PRESENTARSE — {len(rojos)} error(es) crítico(s). "
                   f"Presentar con errores resulta en multa del 70-100% del valor de contribuciones "
                   f"(Art. 197 Ley Aduanera).")
    elif amarillos:
        semaforo = "yellow"
        puede_presentar = True
        resumen = (f"🟡 PUEDE PRESENTARSE CON ADVERTENCIAS — {len(amarillos)} punto(s) a revisar. "
                   f"Se recomienda atender antes de presentar en VUCEM para evitar auditorías.")
    else:
        semaforo = "green"
        puede_presentar = True
        resumen = "🟢 MVE LISTA — Todos los campos requeridos por RGCE están completos y válidos. Lista para presentar en VUCEM."

    return {
        "semaforo": semaforo,
        "errores": errores,
        "puede_presentar": puede_presentar,
        "resumen": resumen,
        "total_errores": len(rojos),
        "total_advertencias": len(amarillos),
    }
