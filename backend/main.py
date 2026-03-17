"""
MYSTIC - API Contable
Fourgea Mexico SA de CV / Triple R Oil Mexico SA de CV
Multi-tenant | 147 calculos fiscales | SAT compliant
"""
import calendar
import os
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, date
from typing import Any, Dict, List, Optional

import redis
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text, Column, String, Boolean, SmallInteger, Date, Text, DateTime as SADateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Session

from calculos import calcular_iva, calcular_isr, calcular_ieps
from calculos_completos_147 import CalculosCompletos147
from database import Base, engine, get_db
from models import (AuditLog, AlertaConfig, CierreMes, Empleado, Factura, Lead,
                    MVE, Nomina, TipoCambio, Usuario, Tenant)
from schemas import (CierreResponse, DashboardResponse, EmpleadoCreate,
                     EmpleadoResponse, FacturaCreate, FacturaResponse,
                     LoginRequest, LoginResponse, NominaCreate, NominaResponse,
                     TenantCreate, TenantResponse, UsuarioCreate,
                     UsuarioResponse)
from security import (create_token, get_current_user, hash_password,
                      require_role, verify_password)

# ── INIT ──
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mystic - API Contable",
    description="Sistema contable multi-tenant para importadores/exportadores. Fourgea & Triple R.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis opcional (no bloquea si no está disponible)
try:
    _redis = redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        decode_responses=True,
        socket_connect_timeout=2,
    )
    _redis.ping()
    REDIS_OK = True
except Exception:
    _redis = None
    REDIS_OK = False


def _audit(db: Session, accion: str, usuario=None, tabla=None, datos=None):
    db.add(AuditLog(
        tenant_id=getattr(usuario, "tenant_id", None),
        usuario_id=getattr(usuario, "id", None),
        accion=accion,
        tabla=tabla,
        datos_nuevos=datos,
    ))


# ═══════════════════════════════════════════════
#  HEALTH
# ═══════════════════════════════════════════════

@app.get("/health", tags=["Sistema"])
async def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "online",
        "db": "ok" if db_ok else "error",
        "redis": "ok" if REDIS_OK else "no_disponible",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ═══════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════

@app.post("/auth/login", response_model=LoginResponse, tags=["Auth"])
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(
        Usuario.email == body.email,
        Usuario.activo == True
    ).first()
    if not usuario or not verify_password(body.password, usuario.password):
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    token = create_token(str(usuario.id), extra={"tenant": str(usuario.tenant_id), "rol": usuario.rol})
    _audit(db, "login", usuario)
    db.commit()
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}


@app.post("/auth/registro", response_model=UsuarioResponse, tags=["Auth"])
async def registro(body: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    usuario = Usuario(
        tenant_id=body.tenant_id,
        email=body.email,
        password=hash_password(body.password),
        nombre=body.nombre,
        rol=body.rol,
        telegram_id=body.telegram_id,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@app.get("/auth/me", response_model=UsuarioResponse, tags=["Auth"])
async def me(current_user: Usuario = Depends(get_current_user)):
    return current_user


# ═══════════════════════════════════════════════
#  TENANTS
# ═══════════════════════════════════════════════

@app.post("/tenants", response_model=TenantResponse, tags=["Tenants"])
async def crear_tenant(body: TenantCreate, db: Session = Depends(get_db)):
    if db.query(Tenant).filter(Tenant.rfc == body.rfc).first():
        raise HTTPException(status_code=400, detail="RFC ya registrado")
    tenant = Tenant(**body.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@app.get("/tenants", response_model=List[TenantResponse], tags=["Tenants"])
async def listar_tenants(
    current_user: Usuario = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return db.query(Tenant).filter(Tenant.activo == True).all()


# ═══════════════════════════════════════════════
#  FACTURAS
# ═══════════════════════════════════════════════

@app.post("/facturas", response_model=FacturaResponse, tags=["Facturas"])
async def crear_factura(
    body: FacturaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    iva = calcular_iva(body.subtotal)
    isr = calcular_isr(body.subtotal)
    ieps = calcular_ieps(body.subtotal, body.producto_tipo or "otro")
    total = body.subtotal + iva - isr
    total_mxn = total * body.tipo_cambio if body.moneda != "MXN" else total

    factura = Factura(
        tenant_id=current_user.tenant_id,
        rfc_emisor=body.rfc_emisor,
        rfc_receptor=body.rfc_receptor,
        subtotal=body.subtotal,
        iva=iva,
        isr=isr,
        ieps=ieps,
        total=total,
        total_mxn=total_mxn,
        tipo=body.tipo,
        moneda=body.moneda,
        tipo_cambio=body.tipo_cambio,
        concepto=body.concepto,
        producto_tipo=body.producto_tipo,
        folio_sat=body.folio_sat,
        uuid_cfdi=body.uuid_cfdi,
        fecha=body.fecha or datetime.utcnow(),
    )
    db.add(factura)
    _audit(db, "crear_factura", current_user, "facturas", {"total": total, "tipo": body.tipo})
    db.commit()
    db.refresh(factura)

    # Invalidar cache de cierre del mes
    if REDIS_OK:
        mes_key = f"cierre:{current_user.tenant_id}:{factura.fecha.year}:{factura.fecha.month}"
        _redis.delete(mes_key)

    return factura


@app.get("/facturas", response_model=List[FacturaResponse], tags=["Facturas"])
async def listar_facturas(
    tipo: Optional[str] = Query(None, description="ingreso | gasto"),
    estado: Optional[str] = Query(None, description="pendiente | pagada | cancelada"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Factura).filter(Factura.tenant_id == current_user.tenant_id)
    if tipo:
        q = q.filter(Factura.tipo == tipo)
    if estado:
        q = q.filter(Factura.estado == estado)
    return q.order_by(Factura.fecha.desc()).offset(offset).limit(limit).all()


@app.get("/facturas/{factura_id}", response_model=FacturaResponse, tags=["Facturas"])
async def obtener_factura(
    factura_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    factura = db.query(Factura).filter(
        Factura.id == factura_id,
        Factura.tenant_id == current_user.tenant_id,
    ).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura


@app.patch("/facturas/{factura_id}/pagar", tags=["Facturas"])
async def pagar_factura(
    factura_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    factura = db.query(Factura).filter(
        Factura.id == factura_id,
        Factura.tenant_id == current_user.tenant_id,
    ).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    factura.estado = "pagada"
    factura.fecha_pago = datetime.utcnow()
    _audit(db, "pagar_factura", current_user, "facturas", {"factura_id": factura_id})
    db.commit()
    return {"mensaje": "Factura marcada como pagada", "id": factura_id}


@app.patch("/facturas/{factura_id}/cancelar", tags=["Facturas"])
async def cancelar_factura(
    factura_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    factura = db.query(Factura).filter(
        Factura.id == factura_id,
        Factura.tenant_id == current_user.tenant_id,
    ).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    factura.estado = "cancelada"
    _audit(db, "cancelar_factura", current_user)
    db.commit()
    return {"mensaje": "Factura cancelada", "id": factura_id}


# ═══════════════════════════════════════════════
#  EMPLEADOS
# ═══════════════════════════════════════════════

@app.post("/empleados", response_model=EmpleadoResponse, tags=["Nomina"])
async def crear_empleado(
    body: EmpleadoCreate,
    current_user: Usuario = Depends(require_role("admin", "rh")),
    db: Session = Depends(get_db),
):
    empleado = Empleado(tenant_id=current_user.tenant_id, **body.model_dump())
    db.add(empleado)
    db.commit()
    db.refresh(empleado)
    return empleado


@app.get("/empleados", response_model=List[EmpleadoResponse], tags=["Nomina"])
async def listar_empleados(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Empleado).filter(
        Empleado.tenant_id == current_user.tenant_id,
        Empleado.activo == True,
    ).all()


# ═══════════════════════════════════════════════
#  NOMINA
# ═══════════════════════════════════════════════

@app.post("/nominas/calcular", response_model=NominaResponse, tags=["Nomina"])
async def calcular_nomina(
    body: NominaCreate,
    current_user: Usuario = Depends(require_role("admin", "rh")),
    db: Session = Depends(get_db),
):
    empleado = db.query(Empleado).filter(
        Empleado.id == body.empleado_id,
        Empleado.tenant_id == current_user.tenant_id,
    ).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # Calculos IMSS 2026
    dias = (body.periodo_fin - body.periodo_inicio).days + 1
    salario_bruto = empleado.salario_diario * dias + body.percepciones_extra

    # IMSS cuotas obrero-patronal (aproximacion)
    imss_trabajador = round(salario_bruto * 0.0175, 2)
    imss_patron = round(salario_bruto * 0.1025, 2)
    infonavit = round(salario_bruto * 0.05, 2)

    # ISR tabla 2026 (simplificado progresivo)
    isr = _calcular_isr_tabla(salario_bruto)

    salario_neto = salario_bruto - imss_trabajador - isr

    nomina = Nomina(
        tenant_id=current_user.tenant_id,
        empleado_id=body.empleado_id,
        periodo_inicio=body.periodo_inicio,
        periodo_fin=body.periodo_fin,
        salario_bruto=salario_bruto,
        imss_trabajador=imss_trabajador,
        imss_patron=imss_patron,
        isr_retenido=isr,
        infonavit=infonavit,
        percepciones_extra=body.percepciones_extra,
        salario_neto=salario_neto,
        calculos_detalle={
            "dias_periodo": dias,
            "salario_diario": empleado.salario_diario,
            "smgv_2026": 278.80,
            "uma_2026": 108.57,
        },
    )
    db.add(nomina)
    db.commit()
    db.refresh(nomina)
    return nomina


def _calcular_isr_tabla(salario: float) -> float:
    """ISR mensual simplificado 2026 (tablas SAT)"""
    if salario <= 746.04:
        return round(salario * 0.0192, 2)
    elif salario <= 6332.05:
        return round(salario * 0.0640, 2)
    elif salario <= 11128.01:
        return round(salario * 0.1088, 2)
    elif salario <= 12935.82:
        return round(salario * 0.16, 2)
    elif salario <= 15487.71:
        return round(salario * 0.1792, 2)
    elif salario <= 31236.49:
        return round(salario * 0.2136, 2)
    elif salario <= 49233.00:
        return round(salario * 0.2352, 2)
    elif salario <= 93993.90:
        return round(salario * 0.30, 2)
    else:
        return round(salario * 0.35, 2)


# ═══════════════════════════════════════════════
#  CIERRE MENSUAL
# ═══════════════════════════════════════════════

@app.get("/cierre/{ano}/{mes}", tags=["Cierre"])
async def cierre_mes(
    ano: int,
    mes: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Cache Redis
    cache_key = f"cierre:{current_user.tenant_id}:{ano}:{mes}"
    if REDIS_OK:
        cached = _redis.get(cache_key)
        if cached:
            import json
            return json.loads(cached)

    primer_dia = datetime(ano, mes, 1)
    ultimo_dia = datetime(ano, mes, calendar.monthrange(ano, mes)[1], 23, 59, 59)

    facturas = db.query(Factura).filter(
        Factura.tenant_id == current_user.tenant_id,
        Factura.fecha >= primer_dia,
        Factura.fecha <= ultimo_dia,
    ).all()

    ingresos = sum(f.total_mxn or f.total for f in facturas if f.tipo == "ingreso")
    gastos = sum(f.total_mxn or f.total for f in facturas if f.tipo == "gasto")
    iva_cobrado = sum(f.iva for f in facturas if f.tipo == "ingreso")
    iva_pagado = sum(f.iva for f in facturas if f.tipo == "gasto")

    datos_calc = {
        "ingresos": ingresos,
        "costo": gastos * 0.7,
        "gastos": gastos * 0.3,
        "impuestos": 0,
        "intereses": 0,
        "deprec": 0,
        "amort": 0,
        "activos": 5000000,
        "patrimonio": 2000000,
    }
    calculos = CalculosCompletos147.generar_cierre_maestro(datos_calc)

    resultado = {
        "periodo": f"{ano}-{mes:02d}",
        "tenant_id": current_user.tenant_id,
        "ingresos": ingresos,
        "gastos": gastos,
        "utilidad_bruta": ingresos - gastos,
        "utilidad_neta": calculos["utilidad_neta"],
        "iva_cobrado": iva_cobrado,
        "iva_pagado": iva_pagado,
        "iva_neto": iva_cobrado - iva_pagado,
        "isr_estimado": calculos["isr"],
        "ptu": calculos["ptu"],
        "ebitda": calculos["ebitda"],
        "margen_neto_pct": calculos["margen_neto"],
        "num_facturas": len(facturas),
        "calculos_147": calculos,
    }

    if REDIS_OK:
        import json
        _redis.setex(cache_key, 3600, json.dumps(resultado, default=str))

    return resultado


@app.post("/cierre/{ano}/{mes}/guardar", response_model=CierreResponse, tags=["Cierre"])
async def guardar_cierre(
    ano: int,
    mes: int,
    current_user: Usuario = Depends(require_role("admin", "contador", "ceo")),
    db: Session = Depends(get_db),
):
    existente = db.query(CierreMes).filter(
        CierreMes.tenant_id == current_user.tenant_id,
        CierreMes.ano == ano,
        CierreMes.mes == mes,
    ).first()
    if existente and existente.estado == "cerrado":
        raise HTTPException(status_code=400, detail="Cierre ya fue cerrado y no puede modificarse")

    datos = await cierre_mes(ano, mes, current_user, db)

    cierre = existente or CierreMes(tenant_id=current_user.tenant_id, ano=ano, mes=mes)
    cierre.total_ingresos = datos["ingresos"]
    cierre.total_gastos = datos["gastos"]
    cierre.utilidad_bruta = datos["utilidad_bruta"]
    cierre.utilidad_neta = datos["utilidad_neta"]
    cierre.iva_cobrado = datos["iva_cobrado"]
    cierre.iva_pagado = datos["iva_pagado"]
    cierre.iva_neto = datos["iva_neto"]
    cierre.isr_total = datos["isr_estimado"]
    cierre.ptu = datos["ptu"]
    cierre.ebitda = datos["ebitda"]
    cierre.margen_neto = datos["margen_neto_pct"]
    cierre.num_facturas = datos["num_facturas"]
    cierre.calculos_completos = datos["calculos_147"]
    cierre.estado = "cerrado"
    cierre.fecha_cierre = datetime.utcnow()

    if not existente:
        db.add(cierre)
    db.commit()
    db.refresh(cierre)
    return cierre


# ═══════════════════════════════════════════════
#  DASHBOARD EJECUTIVO
# ═══════════════════════════════════════════════

@app.get("/dashboard", response_model=DashboardResponse, tags=["Dashboard"])
async def dashboard(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ahora = datetime.utcnow()
    inicio_mes = datetime(ahora.year, ahora.month, 1)

    facturas = db.query(Factura).filter(Factura.tenant_id == current_user.tenant_id).all()
    mes_actual = [f for f in facturas if f.fecha >= inicio_mes]

    ingresos_mes = sum(f.total for f in mes_actual if f.tipo == "ingreso")
    gastos_mes = sum(f.total for f in mes_actual if f.tipo == "gasto")
    por_cobrar = sum(f.total for f in facturas if f.estado == "pendiente" and f.tipo == "ingreso")
    por_pagar = sum(f.total for f in facturas if f.estado == "pendiente" and f.tipo == "gasto")

    alertas = []
    if por_cobrar > 100000:
        alertas.append(f"Cuentas por cobrar altas: ${por_cobrar:,.2f} MXN")
    if por_pagar > por_cobrar * 0.8:
        alertas.append("Alerta: gastos pendientes cerca del nivel de ingresos")
    if ingresos_mes == 0:
        alertas.append("Sin ingresos registrados este mes")

    return {
        "tenant_id": current_user.tenant_id,
        "periodo": f"{ahora.year}-{ahora.month:02d}",
        "resumen": {
            "total_facturas": len(facturas),
            "facturas_mes": len(mes_actual),
            "ingresos_mes": ingresos_mes,
            "gastos_mes": gastos_mes,
            "utilidad_mes": ingresos_mes - gastos_mes,
            "por_cobrar": por_cobrar,
            "por_pagar": por_pagar,
        },
        "alertas": alertas,
        "kpis": {
            "margen_bruto_pct": round((ingresos_mes - gastos_mes) / ingresos_mes * 100, 2) if ingresos_mes > 0 else 0,
            "ratio_cobro_pago": round(por_cobrar / por_pagar, 2) if por_pagar > 0 else 0,
            "salud": "verde" if ingresos_mes > gastos_mes else "amarillo" if ingresos_mes > 0 else "rojo",
        },
    }


# ═══════════════════════════════════════════════
#  TIPO DE CAMBIO
# ═══════════════════════════════════════════════

@app.get("/tipo-cambio/hoy", tags=["Fiscal"])
async def tipo_cambio_hoy(db: Session = Depends(get_db)):
    from datetime import timedelta
    hoy = datetime.utcnow().date()
    ayer = hoy - timedelta(days=1)
    tc_hoy = db.query(TipoCambio).filter(
        TipoCambio.fecha >= datetime(hoy.year, hoy.month, hoy.day)
    ).order_by(TipoCambio.fecha.desc()).first()
    tc_ayer_row = db.query(TipoCambio).filter(
        TipoCambio.fecha >= datetime(ayer.year, ayer.month, ayer.day),
        TipoCambio.fecha < datetime(hoy.year, hoy.month, hoy.day)
    ).order_by(TipoCambio.fecha.desc()).first()
    if tc_hoy:
        return {"fecha": str(tc_hoy.fecha.date() if hasattr(tc_hoy.fecha,'date') else tc_hoy.fecha),
                "usd_mxn": tc_hoy.usd_mxn,
                "usd_mxn_ayer": tc_ayer_row.usd_mxn if tc_ayer_row else None,
                "fuente": tc_hoy.fuente}
    tc_val, fuente = 17.5, "estimado"
    try:
        import urllib.request as _ur, json as _j
        resp = _ur.urlopen("https://open.er-api.com/v6/latest/USD", timeout=5)
        data = _j.loads(resp.read())
        tc_val = round(data["rates"].get("MXN", 17.5), 4)
        fuente = "open.er-api.com"
    except Exception:
        pass
    try:
        new_tc = TipoCambio(fecha=datetime(hoy.year, hoy.month, hoy.day), usd_mxn=tc_val, fuente=fuente)
        db.add(new_tc); db.commit()
    except Exception:
        db.rollback()
    return {"fecha": str(hoy), "usd_mxn": tc_val, "usd_mxn_ayer": None, "fuente": fuente}


# ═══════════════════════════════════════════════
#  STATUS PAGE (pública)
# ═══════════════════════════════════════════════

@app.get("/status", tags=["Sistema"])
async def status_publico(db: Session = Depends(get_db)):
    checks = {"api": "ok", "db": "error", "redis": "error", "timestamp": datetime.utcnow().isoformat()}
    try:
        db.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception:
        pass
    try:
        if REDIS_OK:
            _redis.ping()
            checks["redis"] = "ok"
    except Exception:
        pass
    checks["status"] = "operational" if all(v == "ok" for k, v in checks.items() if k not in ("timestamp", "status")) else "degraded"
    return checks


# ═══════════════════════════════════════════════
#  CARGA CFDI XML (DRAG & DROP)
# ═══════════════════════════════════════════════

CFDI_NS = {
    "cfdi": "http://www.sat.gob.mx/cfd/4",
    "cfdi3": "http://www.sat.gob.mx/cfd/3",
}

def _parsear_cfdi(xml_bytes: bytes) -> dict:
    """Parsea CFDI 4.0 y 3.3, extrae campos clave."""
    root = ET.fromstring(xml_bytes)
    ns = "cfdi" if root.tag.startswith("{http://www.sat.gob.mx/cfd/4}") else "cfdi3"
    tag = lambda t: root.tag.split("}")[0] + "}" + t

    def attr(node, name, default=""):
        return node.get(name, default)

    subtotal = float(attr(root, "SubTotal", "0"))
    total = float(attr(root, "Total", "0"))
    moneda = attr(root, "Moneda", "MXN")
    tipo_cambio = float(attr(root, "TipoCambio", "1") or "1")
    tipo_comprobante = attr(root, "TipoDeComprobante", "I")
    uuid_cfdi = ""
    fecha_str = attr(root, "Fecha", "")

    # Complemento timbrado
    for comp in root.iter():
        if "TimbreFiscalDigital" in comp.tag:
            uuid_cfdi = comp.get("UUID", "")
            break

    # Emisor y Receptor
    emisor = root.find(f"{{{CFDI_NS.get(ns,'')}}}" + "Emisor") or root.find(".//{http://www.sat.gob.mx/cfd/4}Emisor") or root.find(".//{http://www.sat.gob.mx/cfd/3}Emisor")
    receptor = root.find(".//{http://www.sat.gob.mx/cfd/4}Receptor") or root.find(".//{http://www.sat.gob.mx/cfd/3}Receptor")

    rfc_emisor = emisor.get("Rfc", "") if emisor is not None else ""
    nombre_emisor = emisor.get("Nombre", "") if emisor is not None else ""
    rfc_receptor = receptor.get("Rfc", "") if receptor is not None else ""

    # Conceptos
    conceptos = []
    for c in root.iter():
        if "Concepto" in c.tag and "Conceptos" not in c.tag:
            conceptos.append(c.get("Descripcion", ""))

    concepto = conceptos[0] if conceptos else "CFDI importado"

    # Calcular IVA desde traslados
    iva = 0.0
    for t in root.iter():
        if "Traslado" in t.tag:
            tasa = float(t.get("TasaOCuota", "0"))
            base = float(t.get("Base", subtotal))
            if abs(tasa - 0.16) < 0.001:
                iva = round(base * 0.16, 2)
                break
    if iva == 0:
        iva = round(subtotal * 0.16, 2)

    tipo = "ingreso" if tipo_comprobante in ("I",) else "gasto"
    fecha = None
    try:
        fecha = datetime.fromisoformat(fecha_str.replace("T", " ").split(".")[0]) if fecha_str else None
    except Exception:
        pass

    return {
        "rfc_emisor": rfc_emisor,
        "rfc_receptor": rfc_receptor,
        "subtotal": subtotal,
        "iva": iva,
        "total": total,
        "moneda": moneda,
        "tipo_cambio": tipo_cambio,
        "concepto": concepto,
        "uuid_cfdi": uuid_cfdi,
        "tipo": tipo,
        "fecha": fecha,
        "nombre_emisor": nombre_emisor,
    }


@app.post("/facturas/xml", tags=["Facturas"])
async def cargar_cfdi_xml(
    archivo: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Carga un CFDI 4.0 o 3.3 en XML y registra la factura automáticamente."""
    if not archivo.filename.lower().endswith(".xml"):
        raise HTTPException(400, "Solo se aceptan archivos .xml (CFDI)")
    xml_bytes = await archivo.read()
    if len(xml_bytes) > 500_000:
        raise HTTPException(400, "Archivo demasiado grande (máx 500KB)")
    try:
        datos = _parsear_cfdi(xml_bytes)
    except Exception as e:
        raise HTTPException(422, f"XML inválido o no es un CFDI válido: {str(e)}")

    # Verificar duplicado por UUID
    if datos["uuid_cfdi"]:
        existe = db.query(Factura).filter(Factura.uuid_cfdi == datos["uuid_cfdi"]).first()
        if existe:
            raise HTTPException(409, f"CFDI ya registrado (UUID: {datos['uuid_cfdi']})")

    isr = calcular_isr(datos["subtotal"])
    ieps = calcular_ieps(datos["subtotal"], "otro")
    total_calc = datos["subtotal"] + datos["iva"] - isr
    total_mxn = total_calc * datos["tipo_cambio"] if datos["moneda"] != "MXN" else total_calc

    factura = Factura(
        tenant_id=current_user.tenant_id,
        rfc_emisor=datos["rfc_emisor"],
        rfc_receptor=datos["rfc_receptor"],
        subtotal=datos["subtotal"],
        iva=datos["iva"],
        isr=isr,
        ieps=ieps,
        total=total_calc,
        total_mxn=total_mxn,
        tipo=datos["tipo"],
        moneda=datos["moneda"],
        tipo_cambio=datos["tipo_cambio"],
        concepto=datos["concepto"],
        producto_tipo="otro",
        uuid_cfdi=datos["uuid_cfdi"] or None,
        fecha=datos["fecha"] or datetime.utcnow(),
    )
    db.add(factura)
    _audit(db, "cargar_cfdi_xml", current_user, "facturas", {"uuid": datos["uuid_cfdi"], "total": total_calc})
    db.commit()
    db.refresh(factura)

    if REDIS_OK:
        mes_key = f"cierre:{current_user.tenant_id}:{factura.fecha.year}:{factura.fecha.month}"
        _redis.delete(mes_key)

    return {**factura.__dict__, "cfdi_parseado": {k: v for k, v in datos.items() if k != "fecha"}}


# ═══════════════════════════════════════════════
#  GSD TASKS
# ═══════════════════════════════════════════════

class GSDTask(Base):
    __tablename__ = "gsd_tasks"
    __table_args__ = {"extend_existing": True}
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    prioridad = Column(SmallInteger, default=2)
    tipo = Column(String(20), default="mit")
    fecha_objetivo = Column(Date, nullable=True)
    completada = Column(Boolean, default=False)
    completada_at = Column(SADateTime, nullable=True)
    created_at = Column(SADateTime, default=datetime.utcnow)

# Crear tabla si no existe
try:
    GSDTask.__table__.create(bind=engine, checkfirst=True)
except Exception:
    pass


class GSDTaskCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    prioridad: int = 2
    tipo: str = "mit"
    fecha_objetivo: Optional[date] = None


class GSDTaskResponse(BaseModel):
    id: uuid.UUID
    titulo: str
    descripcion: Optional[str]
    prioridad: int
    tipo: str
    fecha_objetivo: Optional[date]
    completada: bool
    created_at: datetime

    class Config:
        from_attributes = True


@app.get("/gsd/tasks", response_model=List[GSDTaskResponse], tags=["GSD"])
async def listar_tasks(
    solo_activas: bool = True,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(GSDTask).filter(GSDTask.tenant_id == current_user.tenant_id)
    if solo_activas:
        q = q.filter(GSDTask.completada == False)
    return q.order_by(GSDTask.prioridad.asc(), GSDTask.created_at.asc()).limit(10).all()


@app.post("/gsd/tasks", response_model=GSDTaskResponse, tags=["GSD"])
async def crear_task(
    body: GSDTaskCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # GSD rule: max 3 MITs activos
    if body.tipo == "mit":
        activos = db.query(GSDTask).filter(
            GSDTask.tenant_id == current_user.tenant_id,
            GSDTask.tipo == "mit",
            GSDTask.completada == False,
        ).count()
        if activos >= 3:
            raise HTTPException(400, "GSD: máximo 3 MITs activos. Completa uno antes de agregar otro.")
    task = GSDTask(tenant_id=current_user.tenant_id, **body.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.patch("/gsd/tasks/{task_id}/done", response_model=GSDTaskResponse, tags=["GSD"])
async def completar_task(
    task_id: uuid.UUID,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(GSDTask).filter(
        GSDTask.id == task_id, GSDTask.tenant_id == current_user.tenant_id
    ).first()
    if not task:
        raise HTTPException(404, "Task no encontrada")
    task.completada = True
    task.completada_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


@app.delete("/gsd/tasks/{task_id}", tags=["GSD"])
async def eliminar_task(
    task_id: uuid.UUID,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(GSDTask).filter(
        GSDTask.id == task_id, GSDTask.tenant_id == current_user.tenant_id
    ).first()
    if not task:
        raise HTTPException(404, "Task no encontrada")
    db.delete(task)
    db.commit()
    return {"ok": True}


# ══════════════════════════════════════════════════════════
# MÓDULO MVE — Manifestación de Valor (Art. 78-A Ley Aduanera)
# Entrada en vigor: 1 abril 2026 (modalidad digital VUCEM)
# ══════════════════════════════════════════════════════════

class MVECreate(BaseModel):
    proveedor_nombre: str
    proveedor_pais: str
    proveedor_tax_id: Optional[str] = None
    proveedor_direccion: Optional[str] = None
    numero_factura: str
    fecha_factura: date
    descripcion_mercancias: str
    fraccion_arancelaria: Optional[str] = None
    cantidad: float
    unidad_medida: str
    incoterm: str                    # FOB, CIF, EXW, CFR, DDP, DAP
    valor_factura: float
    moneda: str = "USD"
    tipo_cambio: Optional[float] = None
    flete: float = 0
    seguro: float = 0
    otros_cargos: float = 0
    descuentos: float = 0
    regalias: float = 0
    asistencias: float = 0
    tasa_igi: float = 0             # % arancel fracción arancelaria
    metodo_valoracion: int = 1
    justificacion_metodo: Optional[str] = None
    hay_vinculacion: bool = False
    justificacion_vinculacion: Optional[str] = None
    notas: Optional[str] = None


class MVEResponse(BaseModel):
    id: uuid.UUID
    proveedor_nombre: str
    proveedor_pais: str
    numero_factura: str
    fecha_factura: date
    descripcion_mercancias: str
    fraccion_arancelaria: Optional[str]
    incoterm: str
    valor_factura: float
    moneda: str
    tipo_cambio: float
    valor_en_aduana: Optional[float]
    igi: float
    iva_importacion: float
    dta: float
    metodo_valoracion: int
    hay_vinculacion: bool
    folio_vucem: Optional[str]
    pedimento_numero: Optional[str]
    estado: str
    created_at: datetime

    class Config:
        from_attributes = True


def _calcular_valor_aduana(incoterm: str, valor: float, tc: float,
                            flete: float, seguro: float, otros: float,
                            descuentos: float, regalias: float, asistencias: float) -> float:
    """Calcula el Valor en Aduana = CIF punto de entrada México"""
    valor_mxn = valor * tc
    ajuste_positivo = (regalias + asistencias) * tc
    ajuste_negativo = descuentos * tc

    # Según Incoterm, sumar lo que falta para llegar a CIF
    if incoterm.upper() == "EXW":
        return valor_mxn + (flete + seguro + otros) - ajuste_negativo + ajuste_positivo
    elif incoterm.upper() == "FOB":
        return valor_mxn + (flete + seguro) - ajuste_negativo + ajuste_positivo
    elif incoterm.upper() == "CFR":
        return valor_mxn + seguro - ajuste_negativo + ajuste_positivo
    elif incoterm.upper() in ("CIF", "CIP"):
        return valor_mxn - ajuste_negativo + ajuste_positivo
    elif incoterm.upper() in ("DDP", "DAP"):
        # DDP incluye impuestos — se restan para obtener base
        return valor_mxn - ajuste_negativo + ajuste_positivo
    else:
        return valor_mxn + (flete + seguro + otros) - ajuste_negativo + ajuste_positivo


@app.get("/mve", response_model=List[MVEResponse], tags=["MVE"])
async def listar_mves(
    estado: Optional[str] = None,
    limit: int = 50,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista todas las MVEs del tenant. Filtra por estado opcional."""
    from models import MVE as MVEModel
    q = db.query(MVEModel).filter(MVEModel.tenant_id == str(current_user.tenant_id))
    if estado:
        q = q.filter(MVEModel.estado == estado)
    return q.order_by(MVEModel.created_at.desc()).limit(limit).all()


@app.post("/mve", response_model=MVEResponse, tags=["MVE"])
async def crear_mve(
    body: MVECreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea nueva Manifestación de Valor con cálculo automático de valor en aduana."""
    from models import MVE as MVEModel

    # Tipo de cambio: usar el del día si no se provee
    tc = body.tipo_cambio
    if not tc or tc <= 0:
        hoy = datetime.utcnow().date()
        tc_row = db.query(TipoCambio).filter(
            TipoCambio.fecha <= datetime.combine(hoy, datetime.min.time())
        ).order_by(TipoCambio.fecha.desc()).first()
        tc = tc_row.usd_mxn if tc_row else 17.5

    valor_aduana = _calcular_valor_aduana(
        body.incoterm, body.valor_factura, tc,
        body.flete, body.seguro, body.otros_cargos,
        body.descuentos, body.regalias, body.asistencias
    )

    # IGI (arancel)
    igi = round(valor_aduana * (body.tasa_igi / 100), 2)

    # DTA: 0.8% del valor en aduana (mínimo $450, máximo $900 MXN — CFF)
    dta_raw = valor_aduana * 0.008
    dta = round(max(450, min(900, dta_raw)), 2)

    # IVA importación: (valor_aduana + IGI + DTA) × 16%
    iva_imp = round((valor_aduana + igi + dta) * 0.16, 2)

    mve = MVEModel(
        tenant_id=current_user.tenant_id,
        proveedor_nombre=body.proveedor_nombre,
        proveedor_pais=body.proveedor_pais,
        proveedor_tax_id=body.proveedor_tax_id,
        proveedor_direccion=body.proveedor_direccion,
        numero_factura=body.numero_factura,
        fecha_factura=datetime.combine(body.fecha_factura, datetime.min.time()),
        descripcion_mercancias=body.descripcion_mercancias,
        fraccion_arancelaria=body.fraccion_arancelaria,
        cantidad=body.cantidad,
        unidad_medida=body.unidad_medida,
        incoterm=body.incoterm.upper(),
        valor_factura=body.valor_factura,
        moneda=body.moneda,
        tipo_cambio=tc,
        valor_factura_mxn=round(body.valor_factura * tc, 2),
        flete=body.flete,
        seguro=body.seguro,
        otros_cargos=body.otros_cargos,
        descuentos=body.descuentos,
        regalias=body.regalias,
        asistencias=body.asistencias,
        valor_en_aduana=round(valor_aduana, 2),
        tasa_igi=body.tasa_igi,
        igi=igi,
        iva_importacion=iva_imp,
        dta=dta,
        metodo_valoracion=body.metodo_valoracion,
        justificacion_metodo=body.justificacion_metodo,
        hay_vinculacion=body.hay_vinculacion,
        justificacion_vinculacion=body.justificacion_vinculacion,
        notas=body.notas,
        estado="lista" if not body.hay_vinculacion else "borrador",
    )
    db.add(mve)
    db.commit()
    db.refresh(mve)
    return mve


@app.get("/mve/{mve_id}", response_model=MVEResponse, tags=["MVE"])
async def detalle_mve(
    mve_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from models import MVE as MVEModel
    mve = db.query(MVEModel).filter(
        MVEModel.id == mve_id, MVEModel.tenant_id == str(current_user.tenant_id)
    ).first()
    if not mve:
        raise HTTPException(404, "MVE no encontrada")
    return mve


@app.patch("/mve/{mve_id}/presentar", tags=["MVE"])
async def presentar_mve_vucem(
    mve_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marca la MVE como enviada a VUCEM y registra la fecha de presentación."""
    from models import MVE as MVEModel
    from datetime import datetime
    mve = db.query(MVEModel).filter(
        MVEModel.id == mve_id, MVEModel.tenant_id == str(current_user.tenant_id)
    ).first()
    if not mve:
        raise HTTPException(404, "MVE no encontrada")
    mve.estado = "enviada_vucem"
    mve.fecha_presentacion_vucem = datetime.utcnow()
    db.commit()
    db.refresh(mve)
    return {
        "id": str(mve.id),
        "estado": mve.estado,
        "fecha_presentacion_vucem": mve.fecha_presentacion_vucem.isoformat() if mve.fecha_presentacion_vucem else None,
    }


@app.patch("/mve/{mve_id}/cancelar", tags=["MVE"])
async def cancelar_mve(
    mve_id: str,
    motivo: str = "Sin motivo",
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancela una MVE. No aplica si ya tiene folio o pedimento cerrado."""
    from models import MVE as MVEModel
    mve = db.query(MVEModel).filter(
        MVEModel.id == mve_id, MVEModel.tenant_id == str(current_user.tenant_id)
    ).first()
    if not mve:
        raise HTTPException(404, "MVE no encontrada")
    if mve.estado in ("con_folio", "pedimento_cerrado"):
        raise HTTPException(400, f"No se puede cancelar MVE en estado '{mve.estado}'")
    mve.estado = "cancelada"
    mve.notas = f"Cancelada: {motivo}"
    db.commit()
    return {"ok": True, "estado": mve.estado}


@app.patch("/mve/{mve_id}/folio", tags=["MVE"])
async def registrar_folio_vucem(
    mve_id: str,
    folio: str,
    pedimento: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Registra el folio VUCEM obtenido tras presentar la MVE en el portal."""
    from models import MVE as MVEModel
    mve = db.query(MVEModel).filter(
        MVEModel.id == mve_id, MVEModel.tenant_id == str(current_user.tenant_id)
    ).first()
    if not mve:
        raise HTTPException(404, "MVE no encontrada")
    mve.folio_vucem = folio
    mve.estado = "con_folio"
    if pedimento:
        mve.pedimento_numero = pedimento
        mve.estado = "pedimento_cerrado"
    db.commit()
    db.refresh(mve)
    return {"ok": True, "folio": folio, "estado": mve.estado}


@app.get("/mve/calcular/preview", tags=["MVE"])
async def calcular_mve_preview(
    valor_factura: float,
    incoterm: str = "FOB",
    moneda: str = "USD",
    tipo_cambio: float = 17.5,
    flete: float = 0,
    seguro: float = 0,
    tasa_igi: float = 0,
    current_user: Usuario = Depends(get_current_user),
):
    """Calcula impuestos de importación en tiempo real (sin guardar)."""
    valor_aduana = _calcular_valor_aduana(incoterm, valor_factura, tipo_cambio,
                                          flete, seguro, 0, 0, 0, 0)
    igi = round(valor_aduana * (tasa_igi / 100), 2)
    dta_raw = valor_aduana * 0.008
    dta = round(max(450, min(900, dta_raw)), 2)
    iva_imp = round((valor_aduana + igi + dta) * 0.16, 2)
    total_pagar = round(igi + dta + iva_imp, 2)

    return {
        "valor_factura_mxn": round(valor_factura * tipo_cambio, 2),
        "valor_en_aduana": round(valor_aduana, 2),
        "igi": igi,
        "dta": dta,
        "iva_importacion": iva_imp,
        "total_a_pagar_aduana": total_pagar,
        "desglose": {
            "formula_aduana": f"({round(valor_aduana,2)} + {igi} IGI + {dta} DTA) × 16% IVA",
            "incoterm_usado": incoterm.upper(),
            "tipo_cambio": tipo_cambio,
        }
    }


# ═══════════════════════════════════════════════
#  LEADS / CRM
# ═══════════════════════════════════════════════

class LeadCreate(BaseModel):
    nombre: str
    empresa: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    fuente: Optional[str] = "manual"
    estado: Optional[str] = "nuevo"
    notas: Optional[str] = None


class LeadUpdate(BaseModel):
    nombre: Optional[str] = None
    empresa: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    fuente: Optional[str] = None
    estado: Optional[str] = None
    notas: Optional[str] = None


@app.get("/leads", tags=["CRM"])
async def listar_leads(
    estado: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("contador", "ceo", "admin")),
):
    q = db.query(Lead).filter(Lead.tenant_id == str(current_user.tenant_id))
    if estado:
        q = q.filter(Lead.estado == estado)
    leads = q.order_by(Lead.created_at.desc()).limit(min(limit, 200)).all()
    return [
        {
            "id": l.id,
            "nombre": l.nombre,
            "empresa": l.empresa,
            "email": l.email,
            "telefono": l.telefono,
            "fuente": l.fuente,
            "estado": l.estado,
            "notas": l.notas,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in leads
    ]


@app.post("/leads", status_code=201, tags=["CRM"])
async def crear_lead(
    body: LeadCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("contador", "ceo", "admin")),
):
    lead = Lead(
        tenant_id=str(current_user.tenant_id),
        **body.model_dump(exclude_none=True),
    )
    db.add(lead)
    _audit(db, "lead_crear", current_user, datos=body.model_dump())
    db.commit()
    db.refresh(lead)
    return {"ok": True, "id": lead.id, "nombre": lead.nombre}


@app.patch("/leads/{lead_id}", tags=["CRM"])
async def actualizar_lead(
    lead_id: str,
    body: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("contador", "ceo", "admin")),
):
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.tenant_id == str(current_user.tenant_id),
    ).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    for campo, valor in body.model_dump(exclude_none=True).items():
        setattr(lead, campo, valor)
    _audit(db, "lead_actualizar", current_user, datos=body.model_dump(exclude_none=True))
    db.commit()
    return {"ok": True, "id": lead.id, "estado": lead.estado}


@app.delete("/leads/{lead_id}", tags=["CRM"])
async def eliminar_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("ceo", "admin")),
):
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.tenant_id == str(current_user.tenant_id),
    ).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    db.delete(lead)
    _audit(db, "lead_eliminar", current_user)
    db.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════
#  ALERTAS CONFIG
# ═══════════════════════════════════════════════

class AlertaConfigUpdate(BaseModel):
    alerta_manana: Optional[bool] = None
    hora_manana: Optional[str] = None
    alerta_tarde: Optional[bool] = None
    hora_tarde: Optional[str] = None
    canal_telegram: Optional[bool] = None
    canal_email: Optional[bool] = None
    telegram_chat_id: Optional[str] = None
    whatsapp_numero: Optional[str] = None


@app.get("/alertas/config", tags=["Alertas"])
async def get_alerta_config(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    config = db.query(AlertaConfig).filter(
        AlertaConfig.usuario_id == str(current_user.id)
    ).first()
    if not config:
        config = AlertaConfig(
            usuario_id=str(current_user.id),
            tenant_id=str(current_user.tenant_id),
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return {
        "alerta_manana": config.alerta_manana,
        "hora_manana": config.hora_manana,
        "alerta_tarde": config.alerta_tarde,
        "hora_tarde": config.hora_tarde,
        "canal_telegram": config.canal_telegram,
        "canal_email": config.canal_email,
        "telegram_chat_id": config.telegram_chat_id,
        "whatsapp_numero": config.whatsapp_numero,
    }


@app.patch("/alertas/config", tags=["Alertas"])
async def update_alerta_config(
    body: AlertaConfigUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    config = db.query(AlertaConfig).filter(
        AlertaConfig.usuario_id == str(current_user.id)
    ).first()
    if not config:
        config = AlertaConfig(
            usuario_id=str(current_user.id),
            tenant_id=str(current_user.tenant_id),
        )
        db.add(config)
    for campo, valor in body.model_dump(exclude_none=True).items():
        setattr(config, campo, valor)
    db.commit()
    return {"ok": True}


# ═══════════════════════════════════════════════
#  LOGS / AUDITORÍA
# ═══════════════════════════════════════════════

@app.get("/logs", tags=["Sistema"])
async def get_logs(
    limite: int = 50,
    accion: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("contador", "ceo", "admin")),
):
    q = db.query(AuditLog).filter(AuditLog.tenant_id == current_user.tenant_id)
    if accion:
        q = q.filter(AuditLog.accion == accion)
    logs = q.order_by(AuditLog.created_at.desc()).limit(min(limite, 200)).all()

    user_cache = {}
    result = []
    for log in logs:
        uid = log.usuario_id
        if uid and uid not in user_cache:
            u = db.query(Usuario).filter(Usuario.id == uid).first()
            user_cache[uid] = {"nombre": u.nombre if u else "Sistema", "rol": u.rol if u else ""}
        info = user_cache.get(uid, {"nombre": "Sistema", "rol": ""})

        # Extraer detalle legible de datos_nuevos
        datos = log.datos_nuevos or {}
        detalle = ""
        if log.accion == "crear_factura":
            detalle = f"#{datos.get('numero_factura','?')} — {datos.get('concepto','')[:40]}"
        elif log.accion == "login":
            detalle = datos.get("ip", "") or ""
        elif log.accion in ("pagar_factura", "cancelar_factura"):
            detalle = f"Factura #{datos.get('numero_factura','?')}"
        elif log.accion == "crear_mve":
            detalle = f"{datos.get('proveedor_nombre','?')} — {datos.get('numero_factura','')}"
        elif log.accion == "crear_lead":
            detalle = datos.get("nombre", "")

        result.append({
            "id": str(log.id),
            "fecha": log.created_at.strftime("%d/%m/%Y") if log.created_at else "",
            "hora": log.created_at.strftime("%H:%M") if log.created_at else "",
            "accion": log.accion,
            "tabla": log.tabla or "",
            "usuario": info["nombre"],
            "rol": info["rol"],
            "detalle": detalle,
            "datos": datos,
        })
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# ══════════════════════════════════════════════════════════════════════════════
# AI OS — ORQUESTADOR DE AGENTES (agregado 13 Marzo 2026)
# ══════════════════════════════════════════════════════════════════════════════

import sys as _sys
from pathlib import Path as _Path

_APP = _Path(__file__).parent  # /app en Docker, backend/ en local
_sys.path.insert(0, str(_APP))

_orchestrator = None

def _init_orchestrator():
    global _orchestrator
    if _orchestrator is not None:
        return _orchestrator
    try:
        from orchestrator.orchestrator import Orchestrator
        from memory.task_history import TaskHistory
        from memory.knowledge_store import KnowledgeStore
        _data = _APP / ".data"
        _data.mkdir(exist_ok=True)
        _configs = _APP / "configs"
        _orchestrator = Orchestrator.from_config(
            agents_config=str(_configs / "agents.yaml"),
            skills_config=str(_configs / "skills.yaml"),
        )
        _orchestrator.task_history = TaskHistory(persist_path=str(_data / "tasks.json"))
        _orchestrator.knowledge_store = KnowledgeStore(persist_path=str(_data / "knowledge.json"))
    except Exception as _e:
        import warnings
        warnings.warn(f"[AI OS] No inicializado: {_e}")
    return _orchestrator


@app.on_event("startup")
async def _startup_ai_os():
    _init_orchestrator()


class _TaskPayload(BaseModel):
    skill: str
    args: dict = {}


class _TaskRequest(BaseModel):
    id: Optional[str] = None
    agent: Optional[str] = None
    capability: Optional[str] = None
    payload: _TaskPayload


class _SwarmRequest(BaseModel):
    tasks: List[_TaskRequest]


class _KnowledgePut(BaseModel):
    key: str
    value: Any


class _SearchReq(BaseModel):
    query: str
    limit: int = 5


def _orch():
    o = _init_orchestrator()
    if not o:
        raise HTTPException(status_code=503, detail="AI OS no disponible")
    return o


@app.get("/ai/status", tags=["AI OS"])
def ai_status():
    return _orch().status()


@app.get("/ai/agents", tags=["AI OS"])
def ai_agents():
    return [{"name": a.name, "role": a.instance.role, "capabilities": a.capabilities, "skills": a.instance.list_skills()} for a in _orch().agent_registry.list_agents()]


@app.get("/ai/skills", tags=["AI OS"])
def ai_skills():
    return [{"name": s.name, "description": s.description} for s in _orch().skill_registry.list_skills()]


@app.post("/ai/task", tags=["AI OS"])
def ai_task(req: _TaskRequest, current_user=Depends(get_current_user)):
    task = req.model_dump(exclude_none=True)
    task["payload"] = req.payload.model_dump()
    try:
        return _orch().execute_task(task)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/ai/swarm", tags=["AI OS"])
def ai_swarm(req: _SwarmRequest, current_user=Depends(get_current_user)):
    tasks = [{**t.model_dump(exclude_none=True), "payload": t.payload.model_dump()} for t in req.tasks]
    results = _orch().execute_swarm(tasks)
    return {"total": len(results), "results": results}


@app.get("/ai/memory/tasks", tags=["AI OS"])
def ai_mem_tasks(limit: int = 10, current_user=Depends(get_current_user)):
    return [{"task_id": r.task_id, "task": r.task, "result": r.result, "timestamp": r.timestamp} for r in _orch().task_history.recent(limit)]


@app.get("/ai/memory/knowledge", tags=["AI OS"])
def ai_mem_keys(current_user=Depends(get_current_user)):
    return {"keys": _orch().knowledge_store.keys()}


@app.post("/ai/memory/knowledge", tags=["AI OS"])
def ai_mem_put(req: _KnowledgePut, current_user=Depends(get_current_user)):
    _orch().knowledge_store.put(req.key, req.value)
    return {"status": "ok", "key": req.key}


@app.get("/ai/memory/knowledge/{key}", tags=["AI OS"])
def ai_mem_get(key: str, current_user=Depends(get_current_user)):
    v = _orch().knowledge_store.get(key)
    if v is None:
        raise HTTPException(status_code=404, detail=f"Clave '{key}' no encontrada")
    return {"key": key, "value": v}


@app.post("/ai/memory/knowledge/search", tags=["AI OS"])
def ai_mem_search(req: _SearchReq, current_user=Depends(get_current_user)):
    return {"query": req.query, "results": _orch().knowledge_store.search(req.query)}


# ══════════════════════════════════════════════════════════════════════════════
# BRAIN — Ollama local (phi3:mini) + caché Redis
# Endpoint usado por N8N workflows y Bot Telegram
# Arquitectura: Determinístico($0) → Redis Cache($0) → Ollama($0) → Claude(5%)
# ══════════════════════════════════════════════════════════════════════════════

import hashlib as _hashlib
import urllib.request as _urllib_req
import json as _json

_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
_BRAIN_CACHE_TTL = int(os.environ.get("BRAIN_CACHE_TTL", "3600"))  # 1h default

# Contextos predefinidos para consultas frecuentes (capa determinística)
_BRAIN_CONTEXTS = {
    "aranceles-mexico": (
        "Eres un experto en comercio exterior y aduanas de México. "
        "Conoces el Sistema Armonizado de México (TIGIE), IGI, IVA importación, "
        "cuotas compensatorias, NOM, permisos COFEPRIS y SEMARNAT. "
        "Responde de forma concisa y estructurada en español."
    ),
    "contabilidad-mexico": (
        "Eres un contador experto en fiscalidad mexicana. "
        "Conoces ISR, IVA, IMSS, INFONAVIT, CFDI 4.0, SAT, LISR, LIVA. "
        "Da respuestas precisas y cita el artículo legal cuando sea relevante."
    ),
    "default": (
        "Eres Mystic, el asistente inteligente de Sonora Digital Corp. "
        "Ayudas con contabilidad, comercio exterior y gestión empresarial en México. "
        "Responde siempre en español de forma concisa."
    ),
}


class _BrainRequest(BaseModel):
    question: str
    context: str = "default"
    use_cache: bool = True


class _BrainResponse(BaseModel):
    answer: str
    source: str  # "cache" | "ollama" | "error"
    model: str = "phi3-fast"
    cached: bool = False


def _redis_client():
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    return redis.from_url(redis_url, decode_responses=True)


def _cache_key(question: str, context: str) -> str:
    raw = f"{context}:{question.strip().lower()}"
    return "brain:" + _hashlib.md5(raw.encode()).hexdigest()


def _ollama_ask(question: str, context: str) -> str:
    system_prompt = _BRAIN_CONTEXTS.get(context, _BRAIN_CONTEXTS["default"])
    payload = _json.dumps({
        "model": "phi3-fast",  # phi3:mini con num_ctx=1024 para caber en RAM del VPS
        "prompt": question,
        "system": system_prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 256, "num_ctx": 1024},
    }).encode()
    req = _urllib_req.Request(
        f"{_OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with _urllib_req.urlopen(req, timeout=60) as r:
        data = _json.loads(r.read())
    return data.get("response", "").strip()


@app.post("/api/brain/ask", response_model=_BrainResponse, tags=["Brain"])
async def brain_ask(body: _BrainRequest):
    """
    Consulta al cerebro IA (Ollama phi3:mini local).
    Usado por N8N workflows y Bot Telegram.
    Incluye caché Redis para evitar llamadas repetidas.
    """
    key = _cache_key(body.question, body.context)

    # Capa 2: Redis Cache
    if body.use_cache:
        try:
            r = _redis_client()
            cached = r.get(key)
            if cached:
                return _BrainResponse(answer=cached, source="cache", cached=True)
        except Exception:
            pass  # Si Redis falla, continúa a Ollama

    # Capa 3: Ollama local
    try:
        answer = _ollama_ask(body.question, body.context)
        if body.use_cache and answer:
            try:
                r = _redis_client()
                r.setex(key, _BRAIN_CACHE_TTL, answer)
            except Exception:
                pass
        return _BrainResponse(answer=answer, source="ollama", cached=False)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Brain no disponible: {str(e)}")


@app.get("/api/brain/status", tags=["Brain"])
async def brain_status():
    """Estado del cerebro IA — verifica Ollama y modelos disponibles."""
    try:
        req = _urllib_req.Request(f"{_OLLAMA_URL}/api/tags")
        with _urllib_req.urlopen(req, timeout=5) as r:
            data = _json.loads(r.read())
        models = [m["name"] for m in data.get("models", [])]
        return {
            "ollama": "ok",
            "models": models,
            "phi3_ready": "phi3:mini" in models,
        }
    except Exception as e:
        return {"ollama": "error", "detail": str(e), "phi3_ready": False}
