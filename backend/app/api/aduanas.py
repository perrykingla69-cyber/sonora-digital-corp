"""
aduanas.py — Servicios Aduaneros para HERMES

Endpoints disponibles:
GET  /api/aduanas/clasificar?descripcion=...  — Sugiere fracción arancelaria SAT por palabras clave
POST /api/aduanas/pedimento                   — Calcula contribuciones de importación (IVA+IGI+DTA+Prex)
GET  /api/aduanas/vucem/status               — Estado del sistema VUCEM (mock)
POST /api/aduanas/conciliacion               — Concilia pedimentos vs facturas
GET  /api/aduanas/regimenes                  — Lista regímenes aduaneros comunes

Cliente piloto: Fourgea Mexico SA de CV — RFC: FME080820LC2
Giro: Filtración de fluidos industriales (filtros, aceite, válvulas, tuberías, sellos)
"""
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/aduanas", tags=["aduanas"])


# ── Catálogo de fracciones arancelarias (mock SAT) ───────────────────────────
# Aproximado al TIGIE (Tarifa de la Ley de los Impuestos Generales de Importación y Exportación)
# Fracciones relevantes para industria de filtración, aceite y fluidos industriales

FRACCIONES_ARANCELARIAS: dict = {
    "8421.39.99": {
        "descripcion": "Aparatos para filtrar o depurar líquidos, los demás",
        "palabras_clave": ["filtro", "filtros", "filtracion", "filtración", "depurador", "separador líquido"],
        "igi_pct": 5.0,
        "unidad_medida": "PZA",
        "iva_pct": 16.0,
    },
    "8421.29.99": {
        "descripcion": "Aparatos para filtrar o depurar gases, los demás",
        "palabras_clave": ["filtro aire", "filtro gas", "filtro gases", "purificador aire", "separador gas"],
        "igi_pct": 5.0,
        "unidad_medida": "PZA",
        "iva_pct": 16.0,
    },
    "2710.19.99": {
        "descripcion": "Aceites lubricantes y demás aceites de petróleo",
        "palabras_clave": ["aceite", "lubricante", "lubricantes", "aceite mineral", "aceite industrial", "aceite hidráulico"],
        "igi_pct": 0.0,
        "unidad_medida": "LT",
        "iva_pct": 16.0,
    },
    "8481.20.01": {
        "descripcion": "Válvulas para transmisiones oleohidráulicas o neumáticas",
        "palabras_clave": ["valvula", "válvula", "valvulas", "válvulas", "hidráulica", "neumatica", "neumática"],
        "igi_pct": 5.0,
        "unidad_medida": "PZA",
        "iva_pct": 16.0,
    },
    "8481.80.99": {
        "descripcion": "Los demás artículos de grifería y órganos similares para tuberías",
        "palabras_clave": ["grifo", "llave paso", "regulador presion", "regulador de presión", "actuador"],
        "igi_pct": 5.0,
        "unidad_medida": "PZA",
        "iva_pct": 16.0,
    },
    "7304.39.99": {
        "descripcion": "Tubos y perfiles huecos sin soldadura de hierro o acero, los demás",
        "palabras_clave": ["tuberia", "tuberías", "tubo", "tubos", "perfil hueco", "caño", "cañería"],
        "igi_pct": 15.0,
        "unidad_medida": "KG",
        "iva_pct": 16.0,
    },
    "7307.99.99": {
        "descripcion": "Accesorios de tubería de hierro o acero, los demás",
        "palabras_clave": ["accesorio tubería", "codo", "tee", "union tuberia", "conector tubería", "fitting"],
        "igi_pct": 10.0,
        "unidad_medida": "PZA",
        "iva_pct": 16.0,
    },
    "8484.10.01": {
        "descripcion": "Juntas metálicas o de material metálico combinado",
        "palabras_clave": ["junta", "juntas", "empaque", "empaques", "sello mecanico", "sello mecánico", "gasket"],
        "igi_pct": 5.0,
        "unidad_medida": "PZA",
        "iva_pct": 16.0,
    },
    "4016.93.99": {
        "descripcion": "Juntas y empaques de caucho vulcanizado sin endurecer",
        "palabras_clave": ["junta hule", "empaque hule", "sello hule", "o-ring", "oring", "junta caucho", "empaque caucho"],
        "igi_pct": 5.0,
        "unidad_medida": "KG",
        "iva_pct": 16.0,
    },
    "8413.70.99": {
        "descripcion": "Bombas para líquidos, las demás",
        "palabras_clave": ["bomba", "bombas", "bomba centrifuga", "bomba hidráulica", "pump"],
        "igi_pct": 5.0,
        "unidad_medida": "PZA",
        "iva_pct": 16.0,
    },
    "8501.10.01": {
        "descripcion": "Motores eléctricos de potencia inferior o igual a 37.5 W",
        "palabras_clave": ["motor electrico pequeño", "micromotor", "motor dc", "motor paso"],
        "igi_pct": 0.0,
        "unidad_medida": "PZA",
        "iva_pct": 16.0,
    },
    "8501.52.99": {
        "descripcion": "Motores eléctricos de corriente alterna polifásica, los demás",
        "palabras_clave": ["motor electrico", "motor trifasico", "motor trifásico", "motor industrial", "motor ac"],
        "igi_pct": 0.0,
        "unidad_medida": "PZA",
        "iva_pct": 16.0,
    },
    "8543.70.99": {
        "descripcion": "Máquinas y aparatos eléctricos con función propia, los demás",
        "palabras_clave": ["sensor", "sensores", "transductor", "control electronico", "plc", "controlador"],
        "igi_pct": 0.0,
        "unidad_medida": "PZA",
        "iva_pct": 16.0,
    },
    "3926.90.99": {
        "descripcion": "Las demás manufacturas de plástico",
        "palabras_clave": ["plastico", "plástico", "polietileno", "pvc", "nylon", "polipropileno", "pieza plastica"],
        "igi_pct": 10.0,
        "unidad_medida": "KG",
        "iva_pct": 16.0,
    },
    "7318.15.99": {
        "descripcion": "Tornillos, pernos y artículos similares de hierro o acero",
        "palabras_clave": ["tornillo", "tornillos", "perno", "pernos", "birlo", "birlos", "tuerca", "tuercas", "bolt"],
        "igi_pct": 10.0,
        "unidad_medida": "KG",
        "iva_pct": 16.0,
    },
    "7326.90.99": {
        "descripcion": "Las demás manufacturas de hierro o acero",
        "palabras_clave": ["manufactura acero", "pieza acero", "componente acero", "pieza metalica", "pieza metálica"],
        "igi_pct": 10.0,
        "unidad_medida": "KG",
        "iva_pct": 16.0,
    },
    "8421.99.99": {
        "descripcion": "Partes de aparatos para filtrar o depurar, las demás",
        "palabras_clave": ["cartucho", "cartuchos", "elemento filtrante", "media filtrante", "repuesto filtro", "bolsa filtrante"],
        "igi_pct": 5.0,
        "unidad_medida": "PZA",
        "iva_pct": 16.0,
    },
    "3403.19.99": {
        "descripcion": "Preparaciones lubricantes, las demás",
        "palabras_clave": ["grasa", "grasas", "lubricante solido", "grasa industrial", "antioxidante", "anticorrosivo"],
        "igi_pct": 5.0,
        "unidad_medida": "KG",
        "iva_pct": 16.0,
    },
    "8708.99.99": {
        "descripcion": "Partes y accesorios de vehículos automóviles, los demás",
        "palabras_clave": ["refaccion", "refacción", "refacciones", "autopartes", "autoparte", "repuesto vehiculo"],
        "igi_pct": 5.0,
        "unidad_medida": "PZA",
        "iva_pct": 16.0,
    },
    "9026.20.99": {
        "descripcion": "Instrumentos y aparatos para medir o controlar presión",
        "palabras_clave": ["manometro", "manómetro", "presostato", "medidor presion", "medidor de presión", "gauge"],
        "igi_pct": 0.0,
        "unidad_medida": "PZA",
        "iva_pct": 16.0,
    },
}

# Fracción genérica de fallback
FRACCION_GENERICA = {
    "fraccion": "9801.00.01",
    "descripcion": "Mercancías no clasificadas expresamente",
    "igi_pct": 5.0,
    "unidad_medida": "PZA",
    "iva_pct": 16.0,
    "confianza": "baja",
    "nota": "No se encontró coincidencia exacta. Verifique manualmente en el SIAVI SAT.",
}


# ── Catálogo de regímenes aduaneros ──────────────────────────────────────────

REGIMENES = [
    {
        "clave": "IMD",
        "nombre": "Importación Definitiva",
        "descripcion": "Introducción de mercancías extranjeras para permanecer en el país por tiempo ilimitado.",
        "aplica_igi": True,
        "aplica_iva": True,
        "aplica_dta": True,
        "tipo": "importacion",
    },
    {
        "clave": "EXD",
        "nombre": "Exportación Definitiva",
        "descripcion": "Salida de mercancías nacionales o nacionalizadas para permanecer en el extranjero.",
        "aplica_igi": False,
        "aplica_iva": False,
        "aplica_dta": True,
        "tipo": "exportacion",
    },
    {
        "clave": "ITR",
        "nombre": "Importación Temporal para Retornar",
        "descripcion": "Introducción de mercancías extranjeras para ser retornadas al extranjero en el mismo estado.",
        "aplica_igi": False,
        "aplica_iva": False,
        "aplica_dta": True,
        "tipo": "importacion",
    },
    {
        "clave": "IMT",
        "nombre": "Importación Temporal IMMEX / Maquila",
        "descripcion": "Importación temporal de insumos para elaboración, transformación o reparación en programas IMMEX.",
        "aplica_igi": False,
        "aplica_iva": False,
        "aplica_dta": True,
        "tipo": "importacion",
    },
    {
        "clave": "ETR",
        "nombre": "Exportación Temporal para Retornar",
        "descripcion": "Salida temporal de mercancías nacionales para ser retornadas al país.",
        "aplica_igi": False,
        "aplica_iva": False,
        "aplica_dta": True,
        "tipo": "exportacion",
    },
    {
        "clave": "TRA",
        "nombre": "Tránsito Interno",
        "descripcion": "Conducción de mercancías bajo control fiscal entre aduanas del interior del país.",
        "aplica_igi": False,
        "aplica_iva": False,
        "aplica_dta": False,
        "tipo": "transito",
    },
    {
        "clave": "TRX",
        "nombre": "Tránsito Internacional",
        "descripcion": "Conducción de mercancías extranjeras que atraviesan el territorio nacional hacia otro país.",
        "aplica_igi": False,
        "aplica_iva": False,
        "aplica_dta": False,
        "tipo": "transito",
    },
    {
        "clave": "DEP",
        "nombre": "Depósito Fiscal",
        "descripcion": "Introducción de mercancías a almacenes generales de depósito autorizados.",
        "aplica_igi": False,
        "aplica_iva": False,
        "aplica_dta": True,
        "tipo": "especial",
    },
    {
        "clave": "REC",
        "nombre": "Recinto Fiscalizado Estratégico (PITEX/RFE)",
        "descripcion": "Introducción de mercancías a recintos fiscalizados estratégicos para manufactura global.",
        "aplica_igi": False,
        "aplica_iva": False,
        "aplica_dta": True,
        "tipo": "especial",
    },
    {
        "clave": "REP",
        "nombre": "Retorno de Exportación",
        "descripcion": "Retorno al país de mercancías exportadas definitivamente.",
        "aplica_igi": True,
        "aplica_iva": True,
        "aplica_dta": True,
        "tipo": "importacion",
    },
]


# ── Modelos Pydantic ──────────────────────────────────────────────────────────

class PedimentoRequest(BaseModel):
    """Datos para calcular contribuciones de importación de un pedimento."""
    fraccion_arancelaria: str = Field(
        ...,
        description="Fracción arancelaria TIGIE, p.ej. '8421.39.99'",
        example="8421.39.99",
    )
    valor_usd: float = Field(
        ...,
        gt=0,
        description="Valor factura en dólares USD (valor comercial)",
        example=5000.00,
    )
    tipo_cambio: float = Field(
        ...,
        gt=0,
        description="Tipo de cambio DOF del día de pago (MXN por USD)",
        example=17.85,
    )
    peso_kg: float = Field(
        default=0.0,
        ge=0,
        description="Peso bruto total en kilogramos",
        example=120.5,
    )
    regimen: str = Field(
        default="IMD",
        description="Clave de régimen aduanero. Default: IMD (Importación Definitiva)",
        example="IMD",
    )
    igi_override_pct: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Porcentaje IGI manual si se conoce (sobreescribe el del catálogo)",
    )
    seguro_usd: float = Field(
        default=0.0,
        ge=0,
        description="Costo de seguro en USD (incluir para valor aduana correcto)",
    )
    flete_usd: float = Field(
        default=0.0,
        ge=0,
        description="Costo de flete en USD (incluir para valor aduana correcto)",
    )


class OperacionPedimento(BaseModel):
    """Representa un pedimento en la conciliación."""
    folio_pedimento: str = Field(..., description="Número de pedimento SAT, p.ej. '26-23-3680-6000156'")
    valor_usd: float = Field(..., gt=0, description="Valor declarado en USD")
    fecha: str = Field(..., description="Fecha del pedimento (YYYY-MM-DD)")
    aduana: Optional[str] = Field(default=None, description="Clave aduana (p.ej. '264' = Nogales)")
    proveedor: Optional[str] = Field(default=None, description="Nombre del proveedor extranjero")


class OperacionFactura(BaseModel):
    """Representa una factura en la conciliación."""
    uuid_factura: str = Field(..., description="UUID del CFDI de la factura comercial")
    monto_mxn: float = Field(..., gt=0, description="Monto total factura en MXN")
    fecha: str = Field(..., description="Fecha de la factura (YYYY-MM-DD)")
    proveedor: Optional[str] = Field(default=None, description="Nombre del proveedor")
    moneda_origen: str = Field(default="USD", description="Moneda original de la factura")


class ConciliacionRequest(BaseModel):
    """Datos para conciliar pedimentos vs facturas."""
    pedimentos: List[OperacionPedimento] = Field(
        ...,
        description="Lista de pedimentos a conciliar",
        min_length=1,
    )
    facturas: List[OperacionFactura] = Field(
        ...,
        description="Lista de facturas comerciales a conciliar",
        min_length=1,
    )
    tipo_cambio_promedio: float = Field(
        default=17.85,
        gt=0,
        description="Tipo de cambio promedio del periodo para conversión USD→MXN",
    )
    tolerancia_pct: float = Field(
        default=2.0,
        ge=0,
        le=100,
        description="Tolerancia en % para considerar un match válido (default 2%)",
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalizar(texto: str) -> str:
    """Convierte a minúsculas y remueve acentos básicos para comparación."""
    reemplazos = str.maketrans("áéíóúàèìòùäëïöü", "aeiouaeiouaeiou")
    return texto.lower().translate(reemplazos).strip()


def _buscar_fraccion(descripcion: str) -> dict:
    """
    Busca la fracción arancelaria más apropiada para la descripción dada.
    Retorna un dict con fraccion, descripcion, igi_pct, unidad_medida, confianza.
    """
    desc_norm = _normalizar(descripcion)
    mejor_fraccion = None
    mejor_coincidencias = 0

    for fraccion, datos in FRACCIONES_ARANCELARIAS.items():
        coincidencias = 0
        for kw in datos["palabras_clave"]:
            if _normalizar(kw) in desc_norm:
                coincidencias += 1
        if coincidencias > mejor_coincidencias:
            mejor_coincidencias = coincidencias
            mejor_fraccion = (fraccion, datos)

    if mejor_fraccion and mejor_coincidencias > 0:
        fraccion_key, datos = mejor_fraccion
        confianza = "alta" if mejor_coincidencias >= 2 else "media"
        return {
            "fraccion": fraccion_key,
            "descripcion_sat": datos["descripcion"],
            "igi_pct": datos["igi_pct"],
            "unidad_medida": datos["unidad_medida"],
            "iva_pct": datos["iva_pct"],
            "confianza": confianza,
            "palabras_encontradas": mejor_coincidencias,
            "nota": "Clasificación sugerida por HERMES — confirmar con agente aduanal certificado (AA).",
        }

    return FRACCION_GENERICA


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/clasificar", summary="Sugiere fracción arancelaria SAT por descripción")
def clasificar_mercancia(
    descripcion: str = Query(
        ...,
        min_length=3,
        description="Descripción de la mercancía en español",
        example="filtros de aceite industrial para sistema hidráulico",
    )
):
    """
    Analiza la descripción de la mercancía y sugiere la fracción arancelaria
    más apropiada del catálogo TIGIE (Tarifa LIGIE).

    - Busca palabras clave en ~20 categorías comunes para filtración, aceite, válvulas, etc.
    - Retorna fracción SAT, descripción oficial, IGI%, unidad de medida y nivel de confianza.
    - **Siempre confirmar con un Agente Aduanal (AA) certificado antes de usarlo en pedimento real.**

    *Cliente piloto: Fourgea Mexico SA de CV — RFC: FME080820LC2*
    """
    logger.info("Clasificación arancelaria solicitada | descripcion='%s'", descripcion)

    resultado = _buscar_fraccion(descripcion)

    return {
        "ok": True,
        "descripcion_consultada": descripcion,
        "clasificacion": resultado,
        "advertencia": (
            "Datos mock/simulados. No válidos para presentación oficial ante el SAT o aduana. "
            "Verifique en el SIAVI: https://www.siavi.economia.gob.mx"
        ),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/pedimento", summary="Calcula contribuciones de importación de un pedimento")
def calcular_pedimento(datos: PedimentoRequest):
    """
    Simula el cálculo de contribuciones de un pedimento de importación:

    - **Valor aduana (MXN)** = (valor_usd + seguro_usd + flete_usd) × tipo_cambio
    - **IGI** = valor_aduana × IGI% (obtenido del catálogo por fracción, o manual)
    - **DTA** = $839.05 MXN (cuota fija 2024, Art. 49 LFD)
    - **Prex** = $0 (Derecho de Prevalidación Electrónica — incluido en DTA para la mayoría de operaciones)
    - **IVA** = (valor_aduana + IGI + DTA + Prex) × 16%
    - **Total contribuciones** = IGI + DTA + Prex + IVA

    Régimen aplicado por defecto: **IMD** (Importación Definitiva).

    *Cliente piloto: Fourgea Mexico SA de CV — RFC: FME080820LC2*
    """
    logger.info(
        "Cálculo pedimento | fraccion=%s | usd=%.2f | tc=%.4f | regimen=%s",
        datos.fraccion_arancelaria,
        datos.valor_usd,
        datos.tipo_cambio,
        datos.regimen,
    )

    # Determinar IGI%
    if datos.igi_override_pct is not None:
        igi_pct = datos.igi_override_pct
        fuente_igi = "manual"
    elif datos.fraccion_arancelaria in FRACCIONES_ARANCELARIAS:
        igi_pct = FRACCIONES_ARANCELARIAS[datos.fraccion_arancelaria]["igi_pct"]
        fuente_igi = "catalogo_hermes"
    else:
        igi_pct = 5.0
        fuente_igi = "default_5pct"
        logger.warning("Fracción %s no encontrada en catálogo; IGI por defecto 5%%", datos.fraccion_arancelaria)

    # Buscar régimen
    regimen_info = next((r for r in REGIMENES if r["clave"] == datos.regimen), None)
    if regimen_info is None:
        raise HTTPException(
            status_code=422,
            detail=f"Régimen '{datos.regimen}' no reconocido. Consulta GET /api/aduanas/regimenes.",
        )

    # Cálculos base
    valor_factura_mxn: float = datos.valor_usd * datos.tipo_cambio
    valor_seguro_mxn: float = datos.seguro_usd * datos.tipo_cambio
    valor_flete_mxn: float = datos.flete_usd * datos.tipo_cambio
    valor_aduana_mxn: float = valor_factura_mxn + valor_seguro_mxn + valor_flete_mxn

    # Contribuciones
    if regimen_info["aplica_igi"]:
        igi_mxn: float = round(valor_aduana_mxn * (igi_pct / 100), 2)
    else:
        igi_mxn = 0.0

    dta_mxn: float = 839.05 if regimen_info["aplica_dta"] else 0.0
    prex_mxn: float = 0.0  # Prevalidación incluida en DTA para operaciones estándar

    base_iva: float = valor_aduana_mxn + igi_mxn + dta_mxn + prex_mxn

    if regimen_info["aplica_iva"]:
        iva_mxn: float = round(base_iva * 0.16, 2)
    else:
        iva_mxn = 0.0

    total_contribuciones: float = round(igi_mxn + dta_mxn + prex_mxn + iva_mxn, 2)
    costo_total_mxn: float = round(valor_aduana_mxn + total_contribuciones, 2)

    return {
        "ok": True,
        "entrada": {
            "fraccion_arancelaria": datos.fraccion_arancelaria,
            "valor_usd": datos.valor_usd,
            "seguro_usd": datos.seguro_usd,
            "flete_usd": datos.flete_usd,
            "tipo_cambio": datos.tipo_cambio,
            "peso_kg": datos.peso_kg,
            "regimen": datos.regimen,
            "regimen_nombre": regimen_info["nombre"],
        },
        "calculo": {
            "valor_factura_mxn": round(valor_factura_mxn, 2),
            "valor_seguro_mxn": round(valor_seguro_mxn, 2),
            "valor_flete_mxn": round(valor_flete_mxn, 2),
            "valor_aduana_mxn": round(valor_aduana_mxn, 2),
        },
        "contribuciones": {
            "igi_pct": igi_pct,
            "igi_mxn": igi_mxn,
            "fuente_igi": fuente_igi,
            "dta_mxn": dta_mxn,
            "prex_mxn": prex_mxn,
            "base_iva_mxn": round(base_iva, 2),
            "iva_pct": 16.0,
            "iva_mxn": iva_mxn,
            "total_contribuciones_mxn": total_contribuciones,
        },
        "resumen": {
            "costo_total_mxn": costo_total_mxn,
            "costo_total_usd": round(costo_total_mxn / datos.tipo_cambio, 2),
            "contribuciones_sobre_valor_pct": round(
                (total_contribuciones / valor_aduana_mxn) * 100, 2
            ) if valor_aduana_mxn > 0 else 0.0,
        },
        "advertencia": (
            "Cálculo mock/simulado con fines informativos. "
            "No válido como liquidación oficial. Validar con su agente aduanal certificado."
        ),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/vucem/status", summary="Estado del sistema VUCEM (mock)")
def vucem_status():
    """
    Retorna el estado simulado del sistema VUCEM (Ventanilla Única de Comercio Exterior Mexicano).

    - Integración real con VUCEM requiere certificado FIEL vigente y credenciales de acceso.
    - Este endpoint es un mock informativo; la integración real está pendiente de implementación.

    *Cliente piloto: Fourgea Mexico SA de CV — RFC: FME080820LC2*
    """
    logger.info("Consulta VUCEM status solicitada")

    return {
        "ok": True,
        "sistema": "VUCEM",
        "nombre_completo": "Ventanilla Única de Comercio Exterior Mexicano",
        "url_oficial": "https://www.ventanillaunica.gob.mx",
        "estado": {
            "servicio": "mock",
            "sesion_activa": False,
            "certificado_fiel": "no_configurado",
            "ultimo_intento_login": None,
            "disponibilidad_estimada": "No disponible — integración pendiente",
        },
        "modulos_disponibles": [
            {
                "modulo": "Pedimentos",
                "descripcion": "Consulta y gestión de pedimentos ante el SAT",
                "estado": "pendiente_integracion",
            },
            {
                "modulo": "Semáforo Fiscal",
                "descripcion": "Estado de liberación de mercancía en aduana",
                "estado": "pendiente_integracion",
            },
            {
                "modulo": "Reconocimiento Aduanero",
                "descripcion": "Seguimiento de inspección física de mercancías",
                "estado": "pendiente_integracion",
            },
            {
                "modulo": "Documentos Digitales",
                "descripcion": "Envío y recepción de documentos al agente aduanal",
                "estado": "pendiente_integracion",
            },
        ],
        "nota_integracion": (
            "La integración real con VUCEM requiere: "
            "(1) Certificado e.firma (FIEL) vigente del importador, "
            "(2) Registro de usuario en VUCEM, "
            "(3) Acceso al Web Service de VUCEM con token OAuth2. "
            "Contactar al agente aduanal para configurar acceso."
        ),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/conciliacion", summary="Concilia pedimentos vs facturas comerciales")
def conciliar_pedimentos_facturas(datos: ConciliacionRequest):
    """
    Concilia una lista de pedimentos de importación contra facturas comerciales.

    **Lógica de matching:**
    1. Convierte valores de facturas a USD usando `tipo_cambio_promedio`.
    2. Para cada pedimento, busca la factura cuyo valor USD esté dentro de la tolerancia (%).
    3. Clasifica cada operación como: `match`, `sin_factura` o `sin_pedimento`.

    *Cliente piloto: Fourgea Mexico SA de CV — RFC: FME080820LC2*
    """
    logger.info(
        "Conciliación solicitada | pedimentos=%d | facturas=%d | tolerancia=%.1f%%",
        len(datos.pedimentos),
        len(datos.facturas),
        datos.tolerancia_pct,
    )

    tolerancia_factor = datos.tolerancia_pct / 100.0
    facturas_disponibles = list(datos.facturas)  # copia para marcar usadas
    facturas_usadas: set = set()

    matches = []
    pedimentos_sin_factura = []

    for pedimento in datos.pedimentos:
        match_encontrado = None
        mejor_diferencia = float("inf")

        for idx, factura in enumerate(facturas_disponibles):
            if idx in facturas_usadas:
                continue

            # Convertir factura a USD para comparar
            valor_factura_usd = factura.monto_mxn / datos.tipo_cambio_promedio

            diferencia_abs = abs(pedimento.valor_usd - valor_factura_usd)
            diferencia_pct = (diferencia_abs / pedimento.valor_usd) * 100 if pedimento.valor_usd > 0 else 100.0

            if diferencia_pct <= datos.tolerancia_pct and diferencia_abs < mejor_diferencia:
                mejor_diferencia = diferencia_abs
                match_encontrado = (idx, factura, diferencia_pct, diferencia_abs)

        if match_encontrado:
            idx_usado, factura_match, dif_pct, dif_abs = match_encontrado
            facturas_usadas.add(idx_usado)
            matches.append({
                "estado": "match",
                "folio_pedimento": pedimento.folio_pedimento,
                "fecha_pedimento": pedimento.fecha,
                "valor_pedimento_usd": pedimento.valor_usd,
                "uuid_factura": factura_match.uuid_factura,
                "fecha_factura": factura_match.fecha,
                "valor_factura_mxn": factura_match.monto_mxn,
                "valor_factura_usd_equiv": round(factura_match.monto_mxn / datos.tipo_cambio_promedio, 2),
                "diferencia_usd": round(dif_abs, 2),
                "diferencia_pct": round(dif_pct, 2),
                "dentro_tolerancia": True,
            })
        else:
            pedimentos_sin_factura.append({
                "estado": "sin_factura",
                "folio_pedimento": pedimento.folio_pedimento,
                "fecha_pedimento": pedimento.fecha,
                "valor_pedimento_usd": pedimento.valor_usd,
                "proveedor": pedimento.proveedor,
                "aduana": pedimento.aduana,
                "nota": "No se encontró factura comercial dentro de la tolerancia especificada.",
            })

    # Facturas sin pedimento
    facturas_sin_pedimento = []
    for idx, factura in enumerate(facturas_disponibles):
        if idx not in facturas_usadas:
            facturas_sin_pedimento.append({
                "estado": "sin_pedimento",
                "uuid_factura": factura.uuid_factura,
                "fecha_factura": factura.fecha,
                "valor_factura_mxn": factura.monto_mxn,
                "valor_factura_usd_equiv": round(factura.monto_mxn / datos.tipo_cambio_promedio, 2),
                "proveedor": factura.proveedor,
                "nota": "No se encontró pedimento correspondiente dentro de la tolerancia especificada.",
            })

    total_pedimentos = len(datos.pedimentos)
    total_facturas = len(datos.facturas)
    total_matches = len(matches)
    total_sin_factura = len(pedimentos_sin_factura)
    total_sin_pedimento = len(facturas_sin_pedimento)

    valor_total_pedimentos_usd = sum(p.valor_usd for p in datos.pedimentos)
    valor_total_facturas_mxn = sum(f.monto_mxn for f in datos.facturas)
    valor_total_facturas_usd = valor_total_facturas_mxn / datos.tipo_cambio_promedio

    return {
        "ok": True,
        "resumen": {
            "total_pedimentos": total_pedimentos,
            "total_facturas": total_facturas,
            "matches_encontrados": total_matches,
            "pedimentos_sin_factura": total_sin_factura,
            "facturas_sin_pedimento": total_sin_pedimento,
            "porcentaje_conciliado": round((total_matches / total_pedimentos) * 100, 1) if total_pedimentos > 0 else 0.0,
            "tipo_cambio_usado": datos.tipo_cambio_promedio,
            "tolerancia_pct": datos.tolerancia_pct,
        },
        "financiero": {
            "valor_total_pedimentos_usd": round(valor_total_pedimentos_usd, 2),
            "valor_total_facturas_mxn": round(valor_total_facturas_mxn, 2),
            "valor_total_facturas_usd_equiv": round(valor_total_facturas_usd, 2),
            "diferencia_global_usd": round(valor_total_pedimentos_usd - valor_total_facturas_usd, 2),
        },
        "matches": matches,
        "pedimentos_sin_factura": pedimentos_sin_factura,
        "facturas_sin_pedimento": facturas_sin_pedimento,
        "advertencia": (
            "Conciliación mock/simulada. "
            "Para conciliación oficial, validar con el sistema de contabilidad y el agente aduanal."
        ),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/regimenes", summary="Lista de regímenes aduaneros comunes")
def listar_regimenes():
    """
    Retorna el catálogo de regímenes aduaneros reconocidos por el SAT México
    con sus características de contribuciones aplicables.

    *Cliente piloto: Fourgea Mexico SA de CV — RFC: FME080820LC2*
    """
    logger.info("Consulta catálogo de regímenes aduaneros")

    return {
        "ok": True,
        "total": len(REGIMENES),
        "regimenes": REGIMENES,
        "nota": (
            "Catálogo basado en la Ley Aduanera y el Apéndice 2 del Instructivo de llenado del pedimento. "
            "Verifique vigencia en el SAT: https://www.sat.gob.mx/aduanas"
        ),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
