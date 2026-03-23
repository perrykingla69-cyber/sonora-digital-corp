#!/usr/bin/env python3
"""
MYSTIC MCP Server — Expone herramientas fiscales MX al Brain IA y a Claude Code

Herramientas disponibles:
  - calcular_isr(ingresos, deducciones, tipo)
  - calcular_iva(monto, tasa, operacion)
  - calcular_pedimento(fraccion, valor_usd, tipo_cambio, peso_kg, regimen)
  - verificar_cfdi(uuid)
  - buscar_dof(query, dias)
  - consultar_imss(sbc, empleados)
  - calcular_nomina(salario_diario, dias, extras, tabla_isr)
  - buscar_qdrant(query, coleccion)
  - estado_sistema()

Protocolo: MCP (Model Context Protocol) via stdio o HTTP SSE
Compatibilidad: Claude Code, MYSTIC Brain IA, N8N

Uso como stdio MCP:
    python3 server.py

Instalación en Claude Code:
    claude mcp add mystic-fiscal -- python3 /home/mystic/sonora-digital-corp/apps/mcp-server/server.py
"""
from __future__ import annotations

import json
import logging
import os
import sys
import urllib.request as _req
from datetime import date, datetime
from typing import Any

# ── Config ────────────────────────────────────────────────────────────────────
API_URL       = os.getenv("MYSTIC_API_URL",     "http://localhost:8000")
QDRANT_URL    = os.getenv("QDRANT_URL",         "http://localhost:6333")
OLLAMA_URL    = os.getenv("OLLAMA_URL",         "http://localhost:11434")
EMBED_MODEL   = os.getenv("EMBED_MODEL",        "nomic-embed-text")
COLLECTION    = os.getenv("QDRANT_COLLECTION",  "mystic_knowledge")

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
logger = logging.getLogger("mystic-mcp")

# ── Tablas fiscales 2026 ──────────────────────────────────────────────────────

ISR_TABLA_2026_MENSUAL = [
    # (limite_inferior, limite_superior, cuota_fija, tasa_excedente)
    (0.01,        746.04,    0.00,   0.0192),
    (746.05,     6332.05,   14.32,   0.0640),
    (6332.06,   11128.01,  371.83,   0.1088),
    (11128.02,  12935.82,  893.63,   0.1600),
    (12935.83,  15487.71, 1182.88,   0.1792),
    (15487.72,  31236.49, 1640.18,   0.2136),
    (31236.50,  49233.00, 5004.12,   0.2352),
    (49233.01,  93993.90, 9236.89,   0.3000),
    (93993.91, 125325.20, 22665.17,  0.3200),
    (125325.21, 375975.61, 32691.18, 0.3400),
    (375975.62, float("inf"), 117912.32, 0.3500),
]

UMA_2026_DIARIA   = 113.14
UMA_2026_MENSUAL  = 3_439.56
UMA_2026_ANUAL    = 41_274.72
SMGDF_2026        = 278.80
SMGDF_FRONTERA    = 419.88

IMSS_CUOTAS = {
    "em_cuota_fija_patron":       0.0404,   # Enfermedad/Maternidad — cuota fija
    "em_excedente_patron":        0.0110,   # EM sobre excedente 3 UMAs
    "em_dinero_patron":           0.0070,
    "em_dinero_obrero":           0.0025,
    "em_pensionados_patron":      0.0105,
    "iv_patron":                  0.0175,   # Invalidez y Vida
    "iv_obrero":                  0.00625,
    "retiro_patron":              0.0200,
    "cesantia_patron":            0.03150,
    "cesantia_obrero":            0.01125,
    "guarderias_patron":          0.0100,
    "infonavit_patron":           0.0500,
}

TIGIE_ARANCEL = {
    "8421.29.99": {"desc": "Filtros industriales líquidos", "igi": 5.0},
    "8421.39.99": {"desc": "Filtros para gases", "igi": 5.0},
    "8481.80.19": {"desc": "Válvulas de control industrial", "igi": 0.0},
    "8413.60.99": {"desc": "Bombas centrífugas", "igi": 5.0},
    "8544.42.99": {"desc": "Cables eléctricos", "igi": 7.0},
    "8471.30.01": {"desc": "Laptops/computadoras portátiles", "igi": 0.0},
    "6109.10.01": {"desc": "Playeras de algodón", "igi": 15.0},
    "8703.23.01": {"desc": "Vehículos automóviles gasolina", "igi": 0.0},
    "2709.00.01": {"desc": "Petróleo crudo", "igi": 0.0},
    "3004.90.99": {"desc": "Medicamentos n.e.p.", "igi": 0.0},
}


# ── Funciones de herramientas ─────────────────────────────────────────────────

def calcular_isr(
    ingresos: float,
    deducciones: float = 0.0,
    tipo: str = "mensual",
) -> dict:
    """Calcula ISR personas físicas con actividad empresarial o honorarios."""
    base = max(ingresos - deducciones, 0.0)

    tabla = ISR_TABLA_2026_MENSUAL
    factor = 1.0
    if tipo == "anual":
        factor = 12.0
        base_norm = base / 12.0
    else:
        base_norm = base

    isr = 0.0
    for li, ls, cuota, tasa in tabla:
        li_a, ls_a = li * factor, ls * factor
        if base >= li_a:
            excedente = min(base, ls_a) - li_a
            if excedente > 0:
                isr = cuota * factor + excedente * tasa
    else:
        isr = max(isr, 0.0)

    return {
        "ingresos": round(ingresos, 2),
        "deducciones": round(deducciones, 2),
        "base_gravable": round(base, 2),
        "isr_calculado": round(isr, 2),
        "tasa_efectiva_pct": round((isr / ingresos * 100) if ingresos else 0, 2),
        "tipo": tipo,
        "tabla": "ISR 2026",
        "nota": "Cálculo aproximado — sin subsidio al empleo ni ajuste inflacionario",
    }


def calcular_iva(
    monto: float,
    tasa: float = 16.0,
    operacion: str = "venta",
) -> dict:
    """Calcula IVA a trasladar o acreditar."""
    iva = round(monto * tasa / 100, 2)
    total = round(monto + iva, 2)
    return {
        "subtotal": round(monto, 2),
        "tasa_pct": tasa,
        "iva": iva,
        "total": total,
        "operacion": operacion,
        "nota": "Tasa 16% general | 8% zona libre frontera norte | 0% alimentos y medicamentos",
    }


def calcular_pedimento(
    fraccion: str,
    valor_usd: float,
    tipo_cambio: float = 17.5,
    peso_kg: float = 0.0,
    regimen: str = "A1",
    tmec: bool = False,
) -> dict:
    """Calcula contribuciones de importación: IGI + DTA + IVA."""
    valor_aduana_mxn = round(valor_usd * tipo_cambio, 2)

    # IGI (arancel)
    fraccion_info = TIGIE_ARANCEL.get(fraccion, {})
    igi_pct = 0.0 if tmec else fraccion_info.get("igi", 10.0)
    igi_mxn = round(valor_aduana_mxn * igi_pct / 100, 2)

    # DTA (0.8% del valor en aduana, mínimo cuota anual ~$395 MXN en 2026)
    dta_minima = 395.0
    dta_mxn = max(round(valor_aduana_mxn * 0.008, 2), dta_minima)

    # Base IVA
    base_iva = valor_aduana_mxn + igi_mxn + dta_mxn
    iva_mxn = round(base_iva * 0.16, 2)

    total = round(igi_mxn + dta_mxn + iva_mxn, 2)

    return {
        "fraccion": fraccion,
        "descripcion": fraccion_info.get("desc", "Fracción no catalogada"),
        "valor_usd": valor_usd,
        "tipo_cambio": tipo_cambio,
        "valor_aduana_mxn": valor_aduana_mxn,
        "igi_pct": igi_pct,
        "igi_mxn": igi_mxn,
        "dta_mxn": dta_mxn,
        "base_iva_mxn": round(base_iva, 2),
        "iva_mxn": iva_mxn,
        "total_contribuciones_mxn": total,
        "regimen": regimen,
        "tmec_aplicado": tmec,
        "nota": "T-MEC 0% si mercancía de USA/Canadá con certificación de origen. " + (
            "IGI exento por T-MEC." if tmec else f"IGI {igi_pct}% aplicado."
        ),
    }


def calcular_nomina(
    salario_diario: float,
    dias_trabajados: int = 30,
    horas_extra: float = 0.0,
    prima_vacacional: bool = False,
    incluir_imss: bool = True,
) -> dict:
    """Calcula nómina mensual: percepciones, deducciones IMSS e ISR."""
    # Percepciones
    sueldo_base = round(salario_diario * dias_trabajados, 2)
    hora_extra_val = round((salario_diario / 8) * 2.0 * horas_extra, 2)  # doble
    percepciones = sueldo_base + hora_extra_val

    # Prima vacacional (si corresponde)
    prima_vac = 0.0
    if prima_vacacional:
        dias_vacaciones = 12  # mínimo legal
        prima_vac = round(salario_diario * dias_vacaciones * 0.25, 2)
        percepciones += prima_vac

    # IMSS obrero (deducciones del trabajador)
    sbc = salario_diario  # simplificado (SBC = salario diario tabular)
    sbc_mensual = sbc * 30

    imss_obrero = 0.0
    if incluir_imss:
        # EM dinero obrero
        imss_obrero += sbc_mensual * IMSS_CUOTAS["em_dinero_obrero"]
        # IV obrero
        imss_obrero += sbc_mensual * IMSS_CUOTAS["iv_obrero"]
        # Cesantía obrero
        imss_obrero += sbc_mensual * IMSS_CUOTAS["cesantia_obrero"]
        imss_obrero = round(imss_obrero, 2)

    # ISR retenido (tabla mensual)
    base_isr = percepciones - imss_obrero
    isr_calc = calcular_isr(base_isr, tipo="mensual")
    isr_retenido = isr_calc["isr_calculado"]

    neto = round(percepciones - imss_obrero - isr_retenido, 2)

    # Costo patronal IMSS
    costo_patron = 0.0
    if incluir_imss:
        tope_3uma = 3 * UMA_2026_MENSUAL
        # EM cuota fija + excedente
        costo_patron += sbc_mensual * IMSS_CUOTAS["em_cuota_fija_patron"]
        if sbc_mensual > tope_3uma:
            costo_patron += (sbc_mensual - tope_3uma) * IMSS_CUOTAS["em_excedente_patron"]
        costo_patron += sbc_mensual * (
            IMSS_CUOTAS["em_dinero_patron"] +
            IMSS_CUOTAS["em_pensionados_patron"] +
            IMSS_CUOTAS["iv_patron"] +
            IMSS_CUOTAS["retiro_patron"] +
            IMSS_CUOTAS["cesantia_patron"] +
            IMSS_CUOTAS["guarderias_patron"] +
            IMSS_CUOTAS["infonavit_patron"]
        )
        costo_patron = round(costo_patron, 2)

    return {
        "salario_diario": salario_diario,
        "dias_trabajados": dias_trabajados,
        "sueldo_base": sueldo_base,
        "horas_extra_importe": hora_extra_val,
        "prima_vacacional": prima_vac,
        "total_percepciones": round(percepciones, 2),
        "imss_obrero_deduccion": imss_obrero,
        "isr_retenido": round(isr_retenido, 2),
        "neto_pagar": neto,
        "costo_patronal_imss_infonavit": costo_patron,
        "costo_total_empleado": round(percepciones + costo_patron, 2),
        "uma_2026_mensual": UMA_2026_MENSUAL,
        "tabla": "Nómina 2026 — cálculo estimado",
    }


def consultar_imss(sbc_diario: float, num_empleados: int = 1) -> dict:
    """Estima cuotas IMSS patronales para uno o más empleados."""
    sbc_mensual = sbc_diario * 30
    tope = min(sbc_mensual, 25 * UMA_2026_MENSUAL)

    cuota_mensual = tope * (
        IMSS_CUOTAS["em_cuota_fija_patron"] +
        IMSS_CUOTAS["em_dinero_patron"] +
        IMSS_CUOTAS["em_pensionados_patron"] +
        IMSS_CUOTAS["iv_patron"] +
        IMSS_CUOTAS["retiro_patron"] +
        IMSS_CUOTAS["cesantia_patron"] +
        IMSS_CUOTAS["guarderias_patron"] +
        IMSS_CUOTAS["infonavit_patron"]
    )

    return {
        "sbc_diario": sbc_diario,
        "sbc_mensual": round(sbc_mensual, 2),
        "sbc_tope_25umas": round(25 * UMA_2026_MENSUAL, 2),
        "cuota_mensual_por_empleado": round(cuota_mensual, 2),
        "cuota_mensual_total": round(cuota_mensual * num_empleados, 2),
        "cuota_bimestral_total": round(cuota_mensual * 2 * num_empleados, 2),
        "num_empleados": num_empleados,
        "uma_2026": UMA_2026_MENSUAL,
        "pago": "Bimestral los días 17 de: ene, mar, may, jul, sep, nov",
    }


def buscar_qdrant(query: str, coleccion: str = "", top_k: int = 3) -> dict:
    """Busca en Qdrant por similitud semántica."""
    col = coleccion or COLLECTION
    try:
        # Generar embedding
        embed_payload = json.dumps({"model": EMBED_MODEL, "prompt": query}).encode()
        embed_req = _req.Request(
            f"{OLLAMA_URL}/api/embeddings",
            data=embed_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with _req.urlopen(embed_req, timeout=20) as r:
            vector = json.loads(r.read())["embedding"]

        # Buscar en Qdrant
        search_payload = json.dumps({
            "vector": vector,
            "limit": top_k,
            "with_payload": True,
        }).encode()
        search_req = _req.Request(
            f"{QDRANT_URL}/collections/{col}/points/search",
            data=search_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with _req.urlopen(search_req, timeout=10) as r:
            results = json.loads(r.read()).get("result", [])

        return {
            "query": query,
            "coleccion": col,
            "resultados": [
                {
                    "titulo": r["payload"].get("title", ""),
                    "topic": r["payload"].get("topic", ""),
                    "contenido": r["payload"].get("content", "")[:500],
                    "score": round(r["score"], 4),
                }
                for r in results
            ],
        }
    except Exception as e:
        return {"error": str(e), "query": query}


def estado_sistema() -> dict:
    """Estado actual del sistema MYSTIC (API, Qdrant, Ollama)."""
    try:
        with _req.urlopen(f"{API_URL}/status", timeout=5) as r:
            api = json.loads(r.read())
    except Exception as e:
        api = {"error": str(e)}

    try:
        with _req.urlopen(f"{QDRANT_URL}/readyz", timeout=3) as r:
            qdrant = {"status": "ok"}
    except Exception as e:
        qdrant = {"status": "error", "error": str(e)}

    try:
        with _req.urlopen(f"{OLLAMA_URL}/api/tags", timeout=3) as r:
            data = json.loads(r.read())
            ollama = {"status": "ok", "models": [m["name"] for m in data.get("models", [])]}
    except Exception as e:
        ollama = {"status": "error", "error": str(e)}

    return {"api": api, "qdrant": qdrant, "ollama": ollama}


def calendario_sat(mes: int = 0, anio: int = 0) -> dict:
    """Retorna fechas límite SAT del mes dado (por defecto mes actual)."""
    hoy = date.today()
    m = mes or hoy.month
    a = anio or hoy.year

    # Día 17 del mes siguiente
    if m == 12:
        vencimiento = date(a + 1, 1, 17)
    else:
        vencimiento = date(a, m + 1, 17)

    bimestres = {1: "ene-feb", 3: "mar-abr", 5: "may-jun", 7: "jul-ago", 9: "sep-oct", 11: "nov-dic"}
    es_mes_bimestral = m in bimestres

    return {
        "mes": m,
        "anio": a,
        "declaraciones_mensuales": {
            "isr_provisional": str(vencimiento),
            "iva": str(vencimiento),
            "diot": str(vencimiento),
            "retenciones_isr": str(vencimiento),
            "balanza_contabilidad": str(vencimiento).replace("-17", "-25"),
        },
        "imss_bimestral": {
            "aplica": es_mes_bimestral,
            "periodo": bimestres.get(m, ""),
            "vencimiento": str(vencimiento) if es_mes_bimestral else "No aplica este mes",
        },
        "notas": [
            "Si el día 17 cae en sábado, domingo o festivo, el vencimiento se corre al siguiente día hábil",
            f"Hoy: {hoy.isoformat()} | Faltan {(vencimiento - hoy).days} días para el próximo vencimiento",
        ],
    }


# ── MCP Protocol (stdio) ──────────────────────────────────────────────────────

TOOLS = {
    "calcular_isr": {
        "description": "Calcula ISR personas físicas México 2026. Requiere ingresos y opcionalmente deducciones.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ingresos": {"type": "number", "description": "Ingresos brutos en MXN"},
                "deducciones": {"type": "number", "description": "Deducciones autorizadas en MXN", "default": 0},
                "tipo": {"type": "string", "enum": ["mensual", "anual"], "default": "mensual"},
            },
            "required": ["ingresos"],
        },
        "fn": calcular_isr,
    },
    "calcular_iva": {
        "description": "Calcula IVA a trasladar o acreditar. Tasas: 16% general, 8% frontera, 0% alimentos/medicamentos.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "monto": {"type": "number", "description": "Monto base sin IVA en MXN"},
                "tasa": {"type": "number", "description": "Tasa de IVA: 16, 8 o 0", "default": 16},
                "operacion": {"type": "string", "description": "Tipo: venta o compra", "default": "venta"},
            },
            "required": ["monto"],
        },
        "fn": calcular_iva,
    },
    "calcular_pedimento": {
        "description": "Calcula contribuciones de importación: IGI, DTA e IVA para un pedimento aduanal México.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fraccion": {"type": "string", "description": "Fracción arancelaria TIGIE (10 dígitos, ej: 8421.29.99)"},
                "valor_usd": {"type": "number", "description": "Valor en aduana en USD"},
                "tipo_cambio": {"type": "number", "description": "Tipo de cambio USD/MXN", "default": 17.5},
                "peso_kg": {"type": "number", "description": "Peso en kilogramos", "default": 0},
                "regimen": {"type": "string", "description": "Régimen aduanero: A1, V1, IT", "default": "A1"},
                "tmec": {"type": "boolean", "description": "Aplicar preferencia T-MEC (arancel 0%)", "default": False},
            },
            "required": ["fraccion", "valor_usd"],
        },
        "fn": calcular_pedimento,
    },
    "calcular_nomina": {
        "description": "Calcula nómina mensual completa: percepciones, retenciones IMSS e ISR, neto a pagar y costo patronal.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "salario_diario": {"type": "number", "description": "Salario diario en MXN"},
                "dias_trabajados": {"type": "integer", "description": "Días trabajados en el mes", "default": 30},
                "horas_extra": {"type": "number", "description": "Horas extra trabajadas", "default": 0},
                "prima_vacacional": {"type": "boolean", "description": "Incluir prima vacacional", "default": False},
                "incluir_imss": {"type": "boolean", "description": "Calcular cuotas IMSS", "default": True},
            },
            "required": ["salario_diario"],
        },
        "fn": calcular_nomina,
    },
    "consultar_imss": {
        "description": "Estima cuotas IMSS patronales mensuales y bimestrales para N empleados.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sbc_diario": {"type": "number", "description": "Salario Base de Cotización diario en MXN"},
                "num_empleados": {"type": "integer", "description": "Número de empleados", "default": 1},
            },
            "required": ["sbc_diario"],
        },
        "fn": consultar_imss,
    },
    "buscar_qdrant": {
        "description": "Busca conocimiento fiscal en la base vectorial Qdrant de MYSTIC. Retorna chunks relevantes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Pregunta o tema a buscar"},
                "coleccion": {"type": "string", "description": "Colección Qdrant", "default": "mystic_knowledge"},
                "top_k": {"type": "integer", "description": "Número de resultados", "default": 3},
            },
            "required": ["query"],
        },
        "fn": buscar_qdrant,
    },
    "calendario_sat": {
        "description": "Retorna fechas límite de declaraciones SAT para un mes y año dados.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mes": {"type": "integer", "description": "Mes (1-12), default: mes actual"},
                "anio": {"type": "integer", "description": "Año, default: año actual"},
            },
        },
        "fn": calendario_sat,
    },
    "estado_sistema": {
        "description": "Estado en tiempo real del sistema MYSTIC: API, Qdrant, Ollama y modelos disponibles.",
        "inputSchema": {"type": "object", "properties": {}},
        "fn": estado_sistema,
    },
}


def send(obj: dict):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def handle_request(req: dict) -> dict:
    method = req.get("method", "")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "mystic-fiscal",
                    "version": "1.0.0",
                    "description": "Herramientas fiscales México 2026: ISR, IVA, IMSS, pedimentos, nómina, SAT",
                },
            },
        }

    elif method == "tools/list":
        tools_list = []
        for name, meta in TOOLS.items():
            tools_list.append({
                "name": name,
                "description": meta["description"],
                "inputSchema": meta["inputSchema"],
            })
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools_list}}

    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name not in TOOLS:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": f"Herramienta '{tool_name}' no encontrada"},
            }

        try:
            fn = TOOLS[tool_name]["fn"]
            result = fn(**arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                    "isError": False,
                },
            }
        except Exception as e:
            logger.exception(f"Error en herramienta {tool_name}")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                    "isError": True,
                },
            }

    elif method == "notifications/initialized":
        return None  # No response needed

    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Método '{method}' no soportado"},
        }


def main():
    """Loop principal stdio para protocolo MCP."""
    logger.info("MYSTIC MCP Server iniciado (stdio)")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            if resp is not None:
                send(resp)
        except json.JSONDecodeError as e:
            send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}})
        except Exception as e:
            logger.exception("Error inesperado")


if __name__ == "__main__":
    main()
