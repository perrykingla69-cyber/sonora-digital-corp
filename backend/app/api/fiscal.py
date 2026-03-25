"""
fiscal.py — Servicios Fiscales Avanzados para HERMES

Endpoints disponibles:
GET  /api/fiscal/diot/{ano}/{mes}          — Genera DIOT en formato texto plano SAT
POST /api/fiscal/complemento-pago          — Estructura CFDI 2.0 Complemento de Pago
GET  /api/fiscal/scorecard/{tenant_id}     — KPIs financieros por cliente
GET  /api/fiscal/flujo-proyectado          — Proyección flujo de caja 30/60/90 días

Nota: Los datos de proveedores son mock mientras no se conecta la BD real.
"""
import logging
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/fiscal", tags=["fiscal"])


# ── Modelos Pydantic ──────────────────────────────────────────────────────────

class ProveedorDIOT(BaseModel):
    """Registro de un proveedor para la DIOT."""
    tipo_tercero: str = Field(..., description="04=Nacional, 05=Extranjero, 15=Global")
    tipo_operacion: str = Field(..., description="03=Proveedores, 06=Arrendamiento, 85=Otros")
    rfc_tercero: str
    pais: str = Field(default="MEX")
    nacionalidad: str = Field(default="México")
    iva_pagado: float = Field(default=0.0, description="IVA efectivamente pagado al proveedor")
    iva_retenido: float = Field(default=0.0, description="IVA retenido al proveedor")
    iva_devuelto: float = Field(default=0.0, description="IVA devuelto por el proveedor")


class ComplementoPagoRequest(BaseModel):
    """Datos necesarios para generar el complemento de pago CFDI 2.0."""
    uuid_factura_original: str = Field(..., description="UUID del CFDI que se paga")
    monto_pagado: float = Field(..., gt=0, description="Monto del pago en MXN")
    fecha_pago: date = Field(..., description="Fecha en que se realizó el pago")
    forma_pago: str = Field(..., description="Código SAT: 01=Efectivo, 03=Transferencia, 04=Tarjeta, etc.")
    numero_operacion: Optional[str] = Field(None, description="Folio/referencia del banco (opcional)")
    rfc_emisor: Optional[str] = Field(default="FME080820LC2")
    rfc_receptor: Optional[str] = Field(default="XAXX010101000")


class KPIScorecard(BaseModel):
    """KPIs financieros de un tenant."""
    tenant_id: str
    periodo: str
    margen_bruto_pct: float
    dias_promedio_pago: float
    iva_generado_mes: float
    facturas_pendientes: int
    monto_pendiente: float
    facturas_canceladas: int
    monto_cancelado: float
    facturas_cobradas: int
    monto_cobrado: float
    score_salud: str = Field(description="VERDE / AMARILLO / ROJO")


class MovimientoProyectado(BaseModel):
    """Movimiento esperado en el flujo de caja."""
    fecha: date
    tipo: str = Field(description="ingreso / egreso")
    monto: float
    concepto: str
    probabilidad_pct: int = Field(description="0-100, qué tan probable es que ocurra")
    dias_desde_hoy: int


# ── Mock Data — Proveedores DIOT ──────────────────────────────────────────────

PROVEEDORES_MOCK: List[dict] = [
    {
        "tipo_tercero": "04",
        "tipo_operacion": "03",
        "rfc_tercero": "TMX840524KT2",
        "pais": "MEX",
        "nacionalidad": "México",
        "nombre": "Telmex SA de CV",
        "iva_pagado": 2560.00,
        "iva_retenido": 0.00,
        "iva_devuelto": 0.00,
    },
    {
        "tipo_tercero": "04",
        "tipo_operacion": "03",
        "rfc_tercero": "CFE370814QI0",
        "pais": "MEX",
        "nacionalidad": "México",
        "nombre": "CFE Distribución",
        "iva_pagado": 1840.00,
        "iva_retenido": 0.00,
        "iva_devuelto": 0.00,
    },
    {
        "tipo_tercero": "04",
        "tipo_operacion": "06",
        "rfc_tercero": "INM890312AB3",
        "pais": "MEX",
        "nacionalidad": "México",
        "nombre": "Inmobiliaria del Noroeste SA de CV",
        "iva_pagado": 6400.00,
        "iva_retenido": 960.00,
        "iva_devuelto": 0.00,
    },
    {
        "tipo_tercero": "04",
        "tipo_operacion": "03",
        "rfc_tercero": "OPE150304GE3",
        "pais": "MEX",
        "nacionalidad": "México",
        "nombre": "Operadora de Fluidos Industriales SA",
        "iva_pagado": 12800.00,
        "iva_retenido": 0.00,
        "iva_devuelto": 0.00,
    },
    {
        "tipo_tercero": "05",
        "tipo_operacion": "85",
        "rfc_tercero": "XEXX010101000",
        "pais": "USA",
        "nacionalidad": "Estados Unidos",
        "nombre": "Parker Hannifin Corp",
        "iva_pagado": 0.00,
        "iva_retenido": 0.00,
        "iva_devuelto": 0.00,
    },
]

# ── Mock Data — Facturas para scorecard y flujo ───────────────────────────────

FACTURAS_MOCK: List[dict] = [
    {
        "uuid": "A1B2C3D4-0001-0001-0001-000000000001",
        "cliente": "Triple R Oil México",
        "monto": 87000.00,
        "iva": 13920.00,
        "estado": "pendiente",
        "fecha_emision": date.today() - timedelta(days=12),
        "fecha_vencimiento": date.today() + timedelta(days=18),
        "costo_directo": 62000.00,
    },
    {
        "uuid": "A1B2C3D4-0002-0002-0002-000000000002",
        "cliente": "Grupo Filtración Sonora",
        "monto": 43500.00,
        "iva": 6960.00,
        "estado": "pendiente",
        "fecha_emision": date.today() - timedelta(days=5),
        "fecha_vencimiento": date.today() + timedelta(days=55),
        "costo_directo": 29000.00,
    },
    {
        "uuid": "A1B2C3D4-0003-0003-0003-000000000003",
        "cliente": "Distribuidora Noroeste SA",
        "monto": 22000.00,
        "iva": 3520.00,
        "estado": "cobrada",
        "fecha_emision": date.today() - timedelta(days=40),
        "fecha_vencimiento": date.today() - timedelta(days=10),
        "costo_directo": 15000.00,
    },
    {
        "uuid": "A1B2C3D4-0004-0004-0004-000000000004",
        "cliente": "Maquiladora del Pacífico",
        "monto": 18500.00,
        "iva": 2960.00,
        "estado": "cobrada",
        "fecha_emision": date.today() - timedelta(days=25),
        "fecha_vencimiento": date.today() - timedelta(days=2),
        "costo_directo": 11000.00,
    },
    {
        "uuid": "A1B2C3D4-0005-0005-0005-000000000005",
        "cliente": "Industrias Hermosillo SA",
        "monto": 9800.00,
        "iva": 1568.00,
        "estado": "cancelada",
        "fecha_emision": date.today() - timedelta(days=60),
        "fecha_vencimiento": date.today() - timedelta(days=30),
        "costo_directo": 7000.00,
    },
    {
        "uuid": "A1B2C3D4-0006-0006-0006-000000000006",
        "cliente": "Triple R Oil México",
        "monto": 65000.00,
        "iva": 10400.00,
        "estado": "pendiente",
        "fecha_emision": date.today() - timedelta(days=2),
        "fecha_vencimiento": date.today() + timedelta(days=88),
        "costo_directo": 44000.00,
    },
]

EGRESOS_MOCK: List[dict] = [
    {"concepto": "Renta oficina Hermosillo", "monto": 28000.00, "dia_del_mes": 1, "recurrente": True},
    {"concepto": "Nómina quincenal", "monto": 45000.00, "dia_del_mes": 15, "recurrente": True},
    {"concepto": "Nómina quincenal", "monto": 45000.00, "dia_del_mes": 30, "recurrente": True},
    {"concepto": "Pago IMSS/INFONAVIT", "monto": 12000.00, "dia_del_mes": 17, "recurrente": True},
    {"concepto": "CFE y servicios", "monto": 8500.00, "dia_del_mes": 10, "recurrente": True},
]


# ── Endpoint 1: DIOT ─────────────────────────────────────────────────────────

@router.get(
    "/diot/{ano}/{mes}",
    summary="Genera DIOT en formato texto plano SAT",
)
async def generar_diot(ano: int, mes: int):
    """
    Genera la Declaración Informativa de Operaciones con Terceros (DIOT)
    en el formato de texto plano que acepta el capturador del SAT.

    Formato por línea (separado por pipes |):
    tipo_tercero|tipo_operacion|rfc|nombre|pais|nacionalidad|
    monto_16pct|iva_16pct|monto_import_servicios|monto_arrend|monto_otros|
    iva_pagado|iva_retenido|iva_devuelto

    Retorna texto plano; guarda el archivo como .txt para subirlo al SAT.
    """
    if not (1 <= mes <= 12):
        raise HTTPException(status_code=400, detail="Mes debe estar entre 1 y 12")
    if ano < 2020 or ano > 2099:
        raise HTTPException(status_code=400, detail="Año inválido")

    logger.info("Generando DIOT %d/%02d con %d proveedores mock", ano, mes, len(PROVEEDORES_MOCK))

    lineas: List[str] = []

    for prov in PROVEEDORES_MOCK:
        # Calcular base gravable estimada: IVA pagado / 0.16
        base_gravable = round(prov["iva_pagado"] / 0.16, 2) if prov["iva_pagado"] > 0 else 0.0

        # Distribuir montos según tipo de operación
        monto_proveedores = base_gravable if prov["tipo_operacion"] == "03" else 0.0
        monto_arrendamiento = base_gravable if prov["tipo_operacion"] == "06" else 0.0
        monto_otros = base_gravable if prov["tipo_operacion"] == "85" else 0.0

        campos = [
            prov["tipo_tercero"],      # 1. Tipo de tercero
            prov["tipo_operacion"],    # 2. Tipo de operación
            prov["rfc_tercero"],       # 3. RFC
            prov.get("nombre", ""),    # 4. Nombre (vacío para extranjeros sin RFC)
            prov["pais"],              # 5. País
            prov["nacionalidad"],      # 6. Nacionalidad
            f"{monto_proveedores:.2f}",    # 7. Monto actos/actividades 16%
            f"{prov['iva_pagado']:.2f}",   # 8. IVA pagado 16%
            "0.00",                        # 9. Monto importación servicios
            f"{monto_arrendamiento:.2f}",  # 10. Monto arrendamiento
            f"{monto_otros:.2f}",          # 11. Monto otros actos
            f"{prov['iva_pagado']:.2f}",   # 12. IVA pagado efectivamente
            f"{prov['iva_retenido']:.2f}", # 13. IVA retenido
            f"{prov['iva_devuelto']:.2f}", # 14. IVA devuelto
        ]
        lineas.append("|".join(campos))

    contenido = "\n".join(lineas)
    total_iva = sum(p["iva_pagado"] for p in PROVEEDORES_MOCK)

    logger.info("DIOT %d/%02d generada: %d registros, IVA total=%.2f", ano, mes, len(lineas), total_iva)

    return {
        "periodo": f"{ano}/{mes:02d}",
        "total_proveedores": len(PROVEEDORES_MOCK),
        "total_iva_pagado": total_iva,
        "total_iva_retenido": sum(p["iva_retenido"] for p in PROVEEDORES_MOCK),
        "formato_texto_plano": contenido,
        "instrucciones": (
            "Copia el campo 'formato_texto_plano' en un archivo .txt con codificación ANSI. "
            "Súbelo al Capturador de DIOT en sat.gob.mx > Declaraciones > DIOT."
        ),
        "nota": "Datos mock — conectar a BD real antes de declarar ante SAT",
    }


# ── Endpoint 2: Complemento de Pago CFDI 2.0 ─────────────────────────────────

FORMAS_PAGO_SAT = {
    "01": "Efectivo",
    "02": "Cheque nominativo",
    "03": "Transferencia electrónica de fondos",
    "04": "Tarjeta de crédito",
    "05": "Monedero electrónico",
    "06": "Dinero electrónico",
    "28": "Tarjeta de débito",
    "29": "Tarjeta de servicios",
    "99": "Por definir",
}

@router.post(
    "/complemento-pago",
    summary="Genera estructura CFDI 2.0 Complemento de Pago",
)
async def generar_complemento_pago(payload: ComplementoPagoRequest):
    """
    Recibe los datos del pago realizado y devuelve la estructura JSON
    del Complemento de Pago CFDI versión 2.0 lista para ser timbrada
    por un PAC (Proveedor Autorizado de Certificación).

    Forma de pago códigos comunes:
    - 01: Efectivo
    - 03: Transferencia electrónica (SPEI)
    - 04: Tarjeta de crédito
    - 28: Tarjeta de débito
    """
    if payload.forma_pago not in FORMAS_PAGO_SAT:
        raise HTTPException(
            status_code=400,
            detail=f"Forma de pago '{payload.forma_pago}' no reconocida. "
                   f"Válidas: {list(FORMAS_PAGO_SAT.keys())}",
        )

    # Validar formato UUID de la factura original
    try:
        uuid.UUID(payload.uuid_factura_original)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="uuid_factura_original no es un UUID válido (formato: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX)",
        )

    monto = Decimal(str(payload.monto_pagado)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # IVA trasladado sobre el pago (si aplica tasa 16%)
    iva_trasladado = (monto * Decimal("0.16")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    base_iva = monto  # base = monto del pago para traslado

    uuid_nuevo = str(uuid.uuid4()).upper()
    folio_num = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
    fecha_timbrado = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    estructura_cfdi = {
        "cfdi:Comprobante": {
            "@Version": "4.0",
            "@Fecha": f"{payload.fecha_pago}T00:00:00",
            "@Folio": folio_num,
            "@Serie": "P",
            "@TipoDeComprobante": "P",
            "@Exportacion": "01",
            "@SubTotal": "0",
            "@Total": "0",
            "@Moneda": "XXX",
            "@LugarExpedicion": "83000",
            "cfdi:Emisor": {
                "@Rfc": payload.rfc_emisor,
                "@RegimenFiscal": "601",
            },
            "cfdi:Receptor": {
                "@Rfc": payload.rfc_receptor,
                "@UsoCFDI": "CP01",
                "@DomicilioFiscalReceptor": "83000",
                "@RegimenFiscalReceptor": "612",
            },
            "cfdi:Conceptos": {
                "cfdi:Concepto": {
                    "@ClaveProdServ": "84111506",
                    "@Cantidad": "1",
                    "@ClaveUnidad": "ACT",
                    "@Descripcion": "Pago",
                    "@ValorUnitario": "0",
                    "@Importe": "0",
                    "@ObjetoImp": "01",
                }
            },
            "cfdi:Complemento": {
                "pago20:Pagos": {
                    "@Version": "2.0",
                    "pago20:Totales": {
                        "@MontoTotalPagos": str(monto),
                        "@TotalTrasladosBaseIVA16": str(base_iva),
                        "@TotalTrasladosImpuestoIVA16": str(iva_trasladado),
                    },
                    "pago20:Pago": {
                        "@FechaPago": f"{payload.fecha_pago}T12:00:00",
                        "@FormaDePagoP": payload.forma_pago,
                        "@MonedaP": "MXN",
                        "@TipoCambioP": "1",
                        "@Monto": str(monto),
                        "@NumOperacion": payload.numero_operacion or folio_num,
                        "pago20:DoctoRelacionado": {
                            "@IdDocumento": payload.uuid_factura_original.upper(),
                            "@MonedaDR": "MXN",
                            "@NumParcialidad": "1",
                            "@ImpSaldoAnt": str(monto),
                            "@ImpPagado": str(monto),
                            "@ImpSaldoInsoluto": "0.00",
                            "@ObjetoImpDR": "02",
                            "pago20:ImpuestosDR": {
                                "pago20:TrasladosDR": {
                                    "pago20:TrasladoDR": {
                                        "@BaseDR": str(base_iva),
                                        "@ImpuestoDR": "002",
                                        "@TipoFactorDR": "Tasa",
                                        "@TasaOCuotaDR": "0.160000",
                                        "@ImporteDR": str(iva_trasladado),
                                    }
                                }
                            },
                        },
                        "pago20:ImpuestosP": {
                            "pago20:TrasladosP": {
                                "pago20:TrasladoP": {
                                    "@BaseP": str(base_iva),
                                    "@ImpuestoP": "002",
                                    "@TipoFactorP": "Tasa",
                                    "@TasaOCuotaP": "0.160000",
                                    "@ImporteP": str(iva_trasladado),
                                }
                            }
                        },
                    },
                }
            },
        },
        "_meta": {
            "uuid_generado": uuid_nuevo,
            "folio": folio_num,
            "fecha_generacion": fecha_timbrado,
            "forma_pago_descripcion": FORMAS_PAGO_SAT[payload.forma_pago],
            "monto_pago": float(monto),
            "iva_trasladado": float(iva_trasladado),
            "instrucciones": (
                "Envía la estructura 'cfdi:Comprobante' al PAC para timbrado. "
                "El PAC asignará el TimbreFiscalDigital con UUID definitivo y sello."
            ),
            "nota": "UUID en _meta es provisional; el UUID real lo asigna el PAC al timbrar.",
        },
    }

    logger.info(
        "Complemento de pago generado: factura=%s monto=%.2f forma=%s",
        payload.uuid_factura_original,
        float(monto),
        payload.forma_pago,
    )

    return estructura_cfdi


# ── Endpoint 3: Scorecard por Tenant ─────────────────────────────────────────

@router.get(
    "/scorecard/{tenant_id}",
    response_model=KPIScorecard,
    summary="KPIs financieros por cliente/tenant",
)
async def scorecard_tenant(tenant_id: str):
    """
    Calcula y devuelve el dashboard financiero (scorecard) para un tenant.

    KPIs incluidos:
    - Margen bruto estimado
    - Días promedio de pago de clientes
    - IVA generado en el mes actual
    - Conteo y montos de facturas por estado (pendiente, cobrada, cancelada)
    - Score de salud financiera: VERDE / AMARILLO / ROJO
    """
    logger.info("Generando scorecard para tenant_id=%s", tenant_id)

    hoy = date.today()
    inicio_mes = hoy.replace(day=1)

    # Agregar facturas mock (en producción: filtrar por tenant_id)
    pendientes = [f for f in FACTURAS_MOCK if f["estado"] == "pendiente"]
    cobradas = [f for f in FACTURAS_MOCK if f["estado"] == "cobrada"]
    canceladas = [f for f in FACTURAS_MOCK if f["estado"] == "cancelada"]

    # IVA generado en el mes actual (facturas emitidas desde inicio del mes)
    iva_mes = sum(
        f["iva"] for f in FACTURAS_MOCK
        if f["estado"] != "cancelada" and f["fecha_emision"] >= inicio_mes
    )

    # Margen bruto: (ingresos_cobrados - costos_directos) / ingresos_cobrados
    total_cobrado = sum(f["monto"] for f in cobradas)
    costo_cobrado = sum(f["costo_directo"] for f in cobradas)
    margen = ((total_cobrado - costo_cobrado) / total_cobrado * 100) if total_cobrado > 0 else 0.0

    # Días promedio de pago (facturas cobradas: días entre emisión y vencimiento)
    if cobradas:
        dias_pago_lista = [
            (f["fecha_vencimiento"] - f["fecha_emision"]).days for f in cobradas
        ]
        dias_prom = sum(dias_pago_lista) / len(dias_pago_lista)
    else:
        dias_prom = 0.0

    monto_pendiente = sum(f["monto"] for f in pendientes)
    monto_cancelado = sum(f["monto"] for f in canceladas)

    # Score de salud financiera
    if margen >= 30 and dias_prom <= 30 and len(pendientes) <= 3:
        score = "VERDE"
    elif margen >= 15 and dias_prom <= 60:
        score = "AMARILLO"
    else:
        score = "ROJO"

    return KPIScorecard(
        tenant_id=tenant_id,
        periodo=f"{hoy.year}/{hoy.month:02d}",
        margen_bruto_pct=round(margen, 2),
        dias_promedio_pago=round(dias_prom, 1),
        iva_generado_mes=round(iva_mes, 2),
        facturas_pendientes=len(pendientes),
        monto_pendiente=round(monto_pendiente, 2),
        facturas_canceladas=len(canceladas),
        monto_cancelado=round(monto_cancelado, 2),
        facturas_cobradas=len(cobradas),
        monto_cobrado=round(total_cobrado, 2),
        score_salud=score,
    )


# ── Endpoint 4: Flujo de Caja Proyectado ─────────────────────────────────────

@router.get(
    "/flujo-proyectado",
    summary="Proyección de flujo de caja 30/60/90 días",
)
async def flujo_proyectado(
    horizonte: int = Query(default=90, ge=30, le=90, description="Días a proyectar: 30, 60 o 90"),
):
    """
    Proyecta el flujo de caja para los próximos 30, 60 o 90 días.

    Ingresos esperados: basados en facturas pendientes (fecha de vencimiento).
    Egresos esperados: recurrentes fijos (nómina, renta, servicios).

    La probabilidad de cobro se calcula en función de días vencidos:
    - Sin vencer:  90% probabilidad
    - Hasta 30 días vencida: 70%
    - Más de 30 días vencida: 40%
    """
    hoy = date.today()
    fecha_limite = hoy + timedelta(days=horizonte)
    movimientos: List[dict] = []

    # Ingresos: facturas pendientes que vencen dentro del horizonte
    for factura in FACTURAS_MOCK:
        if factura["estado"] != "pendiente":
            continue
        venc = factura["fecha_vencimiento"]
        if venc > fecha_limite:
            continue

        dias_desde_hoy = (venc - hoy).days
        if dias_desde_hoy >= 0:
            prob = 90
        elif dias_desde_hoy >= -30:
            prob = 70
        else:
            prob = 40

        movimientos.append({
            "fecha": venc,
            "tipo": "ingreso",
            "monto": factura["monto"],
            "concepto": f"Cobro factura {factura['uuid'][-8:]} — {factura['cliente']}",
            "probabilidad_pct": prob,
            "dias_desde_hoy": dias_desde_hoy,
        })

    # Egresos recurrentes: nómina, renta, etc.
    fecha_iter = hoy
    while fecha_iter <= fecha_limite:
        for egreso in EGRESOS_MOCK:
            dia_egreso = egreso["dia_del_mes"]
            # Ajustar para meses con menos de 30 días
            import calendar
            ultimo_dia = calendar.monthrange(fecha_iter.year, fecha_iter.month)[1]
            dia_real = min(dia_egreso, ultimo_dia)
            fecha_egreso = fecha_iter.replace(day=dia_real)

            if fecha_egreso < hoy or fecha_egreso > fecha_limite:
                continue
            if fecha_egreso == hoy and any(
                m["fecha"] == fecha_egreso and m["concepto"] == egreso["concepto"]
                for m in movimientos
            ):
                continue

            movimientos.append({
                "fecha": fecha_egreso,
                "tipo": "egreso",
                "monto": egreso["monto"],
                "concepto": egreso["concepto"],
                "probabilidad_pct": 100,
                "dias_desde_hoy": (fecha_egreso - hoy).days,
            })

        # Avanzar al siguiente mes
        siguiente_mes = fecha_iter.month + 1
        siguiente_ano = fecha_iter.year
        if siguiente_mes > 12:
            siguiente_mes = 1
            siguiente_ano += 1
        fecha_iter = fecha_iter.replace(year=siguiente_ano, month=siguiente_mes, day=1)

    # Eliminar duplicados por egreso recurrente
    vistos = set()
    dedup = []
    for m in movimientos:
        key = (str(m["fecha"]), m["tipo"], m["concepto"])
        if key not in vistos:
            vistos.add(key)
            dedup.append(m)

    # Ordenar cronológicamente
    dedup.sort(key=lambda x: x["fecha"])

    # Calcular saldo acumulado proyectado
    saldo_acumulado = 0.0
    for m in dedup:
        if m["tipo"] == "ingreso":
            saldo_acumulado += m["monto"] * (m["probabilidad_pct"] / 100)
        else:
            saldo_acumulado -= m["monto"]
        m["saldo_acumulado_proyectado"] = round(saldo_acumulado, 2)
        # Convertir fecha a string para JSON
        m["fecha"] = m["fecha"].isoformat()

    total_ingresos = sum(
        m["monto"] * m["probabilidad_pct"] / 100
        for m in dedup if m["tipo"] == "ingreso"
    )
    total_egresos = sum(m["monto"] for m in dedup if m["tipo"] == "egreso")

    logger.info(
        "Flujo proyectado %d días: %d movimientos, ingresos=%.2f, egresos=%.2f",
        horizonte, len(dedup), total_ingresos, total_egresos,
    )

    return {
        "horizonte_dias": horizonte,
        "fecha_inicio": hoy.isoformat(),
        "fecha_fin": fecha_limite.isoformat(),
        "resumen": {
            "total_ingresos_esperados": round(total_ingresos, 2),
            "total_egresos_comprometidos": round(total_egresos, 2),
            "saldo_neto_proyectado": round(total_ingresos - total_egresos, 2),
            "total_movimientos": len(dedup),
        },
        "movimientos": dedup,
        "nota": "Ingresos ajustados por probabilidad de cobro. Datos mock — conectar a BD real.",
    }
