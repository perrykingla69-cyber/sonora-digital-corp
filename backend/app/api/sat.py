"""
sat.py — Servicios SAT: verificador CFDI, sandbox, utilidades fiscales
GET  /api/sat/verificar/{uuid}     — verifica CFDI en SAT (sin FIEL)
GET  /api/sat/sandbox/status       — estado del modo sandbox
POST /api/sat/sandbox/factura      — genera factura ficticia en sandbox
GET  /api/sat/calendario           — próximos vencimientos SAT
"""
import logging
import httpx
from datetime import date, datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sat", tags=["sat"])


# ── Verificador de CFDI ──────────────────────────────────────────────
@router.get("/verificar/{uuid_cfdi}")
async def verificar_cfdi(uuid_cfdi: str):
    """
    Verifica si un UUID de CFDI está vigente en el SAT.
    Usa el servicio público de verificación (sin FIEL).
    """
    uuid_clean = uuid_cfdi.strip().upper()
    if len(uuid_clean) != 36 or uuid_clean.count("-") != 4:
        raise HTTPException(400, "UUID inválido. Formato: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX")

    # Servicio público SAT (SOAP simplificado vía URL pública)
    sat_url = (
        "https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx"
        f"?id={uuid_clean}&re=XAXX010101000&rr=XAXX010101000&tt=0.00&fe="
    )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(sat_url, follow_redirects=True)
            html = resp.text.lower()

            # Detectar estado en la respuesta HTML del SAT
            if "vigente" in html or "s - comprobante obtenido exitosamente" in html:
                estado = "vigente"
            elif "cancelado" in html:
                estado = "cancelado"
            elif "no encontrado" in html or "no existe" in html:
                estado = "no_encontrado"
            else:
                estado = "indeterminado"

        return {
            "ok": True,
            "uuid": uuid_clean,
            "estado": estado,
            "verificado_en": datetime.utcnow().isoformat(),
            "fuente": "SAT México",
        }
    except httpx.TimeoutException:
        raise HTTPException(504, "SAT no responde. Intenta en unos minutos.")
    except Exception as e:
        logger.error(f"Error verificando CFDI {uuid_cfdi}: {e}")
        raise HTTPException(500, f"Error consultando SAT: {e}")


# ── Sandbox / Demo mode ──────────────────────────────────────────────
SANDBOX_RFC = "XAXX010101000"
SANDBOX_EMPRESA = "EMPRESA DEMO HERMES"

@router.get("/sandbox/status")
async def sandbox_status():
    """Estado del entorno sandbox para demos y pruebas."""
    return {
        "sandbox_activo": True,
        "rfc_prueba": SANDBOX_RFC,
        "empresa": SANDBOX_EMPRESA,
        "nota": "Las facturas sandbox NO se timbran en el SAT. Solo para pruebas.",
        "folios_disponibles": 999,
        "funciones_disponibles": [
            "Generar CFDI ficticios",
            "Simular cierres mensuales",
            "Probar cálculos de IVA/ISR",
            "Validar layouts de nómina",
        ]
    }


class SandboxFacturaRequest(BaseModel):
    concepto: str = "Servicios de prueba"
    subtotal: float = 1000.00
    receptor_nombre: str = "CLIENTE DEMO"
    receptor_rfc: str = "XAXX010101000"


@router.post("/sandbox/factura")
async def sandbox_factura(req: SandboxFacturaRequest):
    """Genera una factura ficticia para demo (no se timbra en SAT)."""
    import uuid as _uuid
    iva = round(req.subtotal * 0.16, 2)
    total = round(req.subtotal + iva, 2)

    return {
        "ok": True,
        "sandbox": True,
        "cfdi": {
            "uuid": str(_uuid.uuid4()).upper(),
            "folio": f"DEMO-{_uuid.uuid4().hex[:6].upper()}",
            "emisor": {"rfc": SANDBOX_RFC, "nombre": SANDBOX_EMPRESA},
            "receptor": {"rfc": req.receptor_rfc, "nombre": req.receptor_nombre},
            "concepto": req.concepto,
            "subtotal": req.subtotal,
            "iva": iva,
            "total": total,
            "fecha": datetime.utcnow().isoformat(),
            "estado": "SANDBOX — No válido ante SAT",
        }
    }


# ── Calendario fiscal SAT ─────────────────────────────────────────────
@router.get("/calendario")
async def calendario_fiscal():
    """Próximos vencimientos fiscales SAT para el mes actual."""
    hoy = date.today()
    mes = hoy.month
    anio = hoy.year

    # Día 17 = declaraciones mensuales (IVA, ISR retenciones)
    # Último día hábil = PTU, anual
    vencimientos = [
        {
            "fecha": f"{anio}-{mes:02d}-17",
            "obligacion": "Declaración mensual IVA + ISR retenciones",
            "aplica_a": ["personas_morales", "personas_fisicas_actividad_empresarial"],
            "urgente": (date(anio, mes, 17) - hoy).days <= 7,
            "dias_restantes": (date(anio, mes, 17) - hoy).days,
        },
        {
            "fecha": f"{anio}-{mes:02d}-17",
            "obligacion": "Pago provisional ISR personas morales",
            "aplica_a": ["personas_morales"],
            "urgente": (date(anio, mes, 17) - hoy).days <= 7,
            "dias_restantes": (date(anio, mes, 17) - hoy).days,
        },
        {
            "fecha": f"{anio}-{mes:02d}-28",
            "obligacion": "IMSS — pago bimestral patrones",
            "aplica_a": ["patrones_con_empleados"],
            "urgente": (date(anio, mes, 28) - hoy).days <= 7,
            "dias_restantes": (date(anio, mes, 28) - hoy).days,
        },
    ]

    # Filtrar solo futuros o de hoy
    vencimientos = [v for v in vencimientos if v["dias_restantes"] >= 0]

    return {
        "mes": f"{anio}-{mes:02d}",
        "hoy": hoy.isoformat(),
        "vencimientos": vencimientos,
        "alertas_urgentes": sum(1 for v in vencimientos if v["urgente"]),
    }
