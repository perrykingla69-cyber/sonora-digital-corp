"""
MYSTIC - API Contable
Fourgea Mexico SA de CV / Triple R Oil Mexico SA de CV
Multi-tenant | 147 calculos fiscales | SAT compliant
"""
import calendar
import os
import sys
import uuid
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime, date
from typing import Any, Dict, List, Optional

import redis
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text, Column, String, Boolean, SmallInteger, Date, Text, DateTime as SADateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Session

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from calculos import calcular_iva, calcular_isr, calcular_ieps
from calculos_completos_147 import CalculosCompletos147
from database import Base, engine, get_db
from models import (AuditLog, AlertaConfig, BrainFeedback, BrainSession,
                    CierreMes, Contacto, Empleado, Factura, Lead,
                    MVE, Nomina, TipoCambio, Usuario, Tenant)
from schemas import (CierreResponse, ContactoCreate, ContactoResponse,
                     DashboardResponse, EmpleadoCreate,
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

# ── Media router (OCR + Whisper STT) ─────────────────────────────────
try:
    from app.api.media import router as media_router
    app.include_router(media_router)
except Exception as _e:
    import logging
    logging.getLogger(__name__).warning(f"Media router no disponible: {_e}")

# ── SAT router (verificador CFDI, sandbox, calendario) ───────────────
try:
    from app.api.sat import router as sat_router
    app.include_router(sat_router)
except Exception as _e:
    import logging
    logging.getLogger(__name__).warning(f"SAT router no disponible: {_e}")

# ── Fiscal router (DIOT, complemento pago, scorecard, flujo) ─────────
try:
    from app.api.fiscal import router as fiscal_router
    app.include_router(fiscal_router)
except Exception as _e:
    import logging
    logging.getLogger(__name__).warning(f"Fiscal router no disponible: {_e}")

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
        recurso=tabla,
        detalle=datos,
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
    if not usuario or not verify_password(body.password, usuario.password_hash):
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
        password_hash=hash_password(body.password),
        nombre=body.nombre,
        rol=body.rol,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@app.get("/auth/me", response_model=UsuarioResponse, tags=["Auth"])
async def me(current_user: Usuario = Depends(get_current_user)):
    return current_user


@app.post("/auth/forgot-password", tags=["Auth"])
async def forgot_password(body: dict, db: Session = Depends(get_db)):
    email = body.get("email", "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email requerido")
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    # Siempre responder igual para no revelar si el email existe
    if not usuario:
        return {"ok": True, "mensaje": "Si el correo existe, recibirás la nueva contraseña por WhatsApp"}

    import secrets, string
    chars = string.ascii_letters + string.digits
    temp_pass = "".join(secrets.choice(chars) for _ in range(10))
    usuario.password_hash = hash_password(temp_pass)
    db.commit()

    # Enviar por WhatsApp si hay número registrado
    wa_sent = False
    wa_numbers = {"cp.nathalyhermosillo@gmail.com": "526622681111", "marco@fourgea.mx": "526623538272"}
    wa_num = wa_numbers.get(email)
    if wa_num:
        try:
            import urllib.request as _ur, json as _j
            payload = _j.dumps({"to": wa_num, "message": f"🔐 Mystic — Contraseña temporal: *{temp_pass}*\nCámbiala después de ingresar."}).encode()
            req = _ur.Request("http://localhost:3001/send", data=payload,
                              headers={"Content-Type": "application/json", "x-api-key": "MysticWA2026!"})
            _ur.urlopen(req, timeout=5)
            wa_sent = True
        except Exception:
            pass

    return {"ok": True, "wa_sent": wa_sent,
            "mensaje": "Contraseña enviada por WhatsApp" if wa_sent else "Contacta a tu administrador: sonoradigitalcorp@gmail.com"}


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
    # Calcular IVA si no viene en el body
    iva = body.iva if body.iva else calcular_iva(body.subtotal)
    total = body.total if body.total else (body.subtotal + iva)

    factura = Factura(
        tenant_id=current_user.tenant_id,
        folio=body.folio,
        uuid_cfdi=body.uuid_cfdi,
        rfc_emisor=body.rfc_emisor,
        rfc_receptor=body.rfc_receptor,
        nombre_emisor=body.nombre_emisor,
        nombre_receptor=body.nombre_receptor,
        subtotal=body.subtotal,
        iva=iva,
        total=total,
        tipo=body.tipo,
        moneda=body.moneda,
        tipo_cambio=body.tipo_cambio,
        estado=body.estado,
        concepto=body.concepto,
        fecha_emision=body.fecha_emision or datetime.utcnow(),
    )
    db.add(factura)
    _audit(db, "crear_factura", current_user, "facturas", {"total": total, "tipo": body.tipo})
    db.commit()
    db.refresh(factura)

    # Invalidar cache de cierre del mes
    if REDIS_OK:
        mes_key = f"cierre:{current_user.tenant_id}:{factura.fecha_emision.year}:{factura.fecha_emision.month}"
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
    return q.order_by(Factura.fecha_emision.desc()).offset(offset).limit(limit).all()


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
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = body.model_dump()
    # Calcular salario_diario y salario_integrado automáticamente
    sal_mensual = data.get("salario_mensual", 0.0)
    fi = data.get("factor_integracion", 1.0452)
    sal_diario = round(sal_mensual / 30.4, 4)
    sal_integrado = round(sal_diario * fi, 4)
    data["salario_diario"] = sal_diario
    data["salario_integrado"] = sal_integrado
    empleado = Empleado(tenant_id=current_user.tenant_id, **data)
    db.add(empleado)
    db.commit()
    db.refresh(empleado)
    return empleado


@app.get("/empleados", response_model=List[EmpleadoResponse], tags=["Nomina"])
async def listar_empleados(
    incluir_bajas: bool = False,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Empleado).filter(Empleado.tenant_id == current_user.tenant_id)
    if not incluir_bajas:
        q = q.filter(Empleado.activo == True)
    return q.order_by(Empleado.nombre).all()


@app.get("/empleados/{empleado_id}", response_model=EmpleadoResponse, tags=["Nomina"])
async def obtener_empleado(
    empleado_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    e = db.query(Empleado).filter(Empleado.id == empleado_id, Empleado.tenant_id == current_user.tenant_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return e


@app.patch("/empleados/{empleado_id}", response_model=EmpleadoResponse, tags=["Nomina"])
async def actualizar_empleado(
    empleado_id: str,
    body: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    e = db.query(Empleado).filter(Empleado.id == empleado_id, Empleado.tenant_id == current_user.tenant_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    for k, v in body.items():
        if hasattr(e, k):
            setattr(e, k, v)
    # Recalcular salarios si se actualiza salario_mensual
    if "salario_mensual" in body:
        fi = getattr(e, "factor_integracion", 1.0452) or 1.0452
        e.salario_diario = round(e.salario_mensual / 30.4, 4)
        e.salario_integrado = round(e.salario_diario * fi, 4)
    db.commit()
    db.refresh(e)
    return e


@app.delete("/empleados/{empleado_id}", tags=["Nomina"])
async def dar_baja_empleado(
    empleado_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import timezone as _tz
    e = db.query(Empleado).filter(Empleado.id == empleado_id, Empleado.tenant_id == current_user.tenant_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    e.activo = False
    e.fecha_baja = datetime.now(_tz.utc)
    db.commit()
    return {"ok": True, "mensaje": f"{e.nombre} dado de baja"}


@app.get("/nomina/calculos/{empleado_id}", tags=["Nomina"])
async def preview_nomina(
    empleado_id: str,
    dias: int = 30,
    percepciones_extra: float = 0.0,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cálculo en tiempo real de nómina: IMSS, ISR, INFONAVIT, neto."""
    e = db.query(Empleado).filter(Empleado.id == empleado_id, Empleado.tenant_id == current_user.tenant_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    UMA_2026 = 108.57
    SMG_2026 = 278.80

    sal_bruto = round((e.salario_diario or 0) * dias + percepciones_extra, 2)
    sal_integrado_dia = e.salario_integrado or e.salario_diario or 0

    # ── IMSS cuotas obreras (trabajador) 2026 ──
    # Enfermedad y maternidad cuota fija
    cuota_fija = round(UMA_2026 * 0.204 * (dias / 30), 2)
    # Excedente sobre 3 UMA
    excedente_base = max(0, sal_integrado_dia - UMA_2026 * 3) * dias
    cuota_excedente = round(excedente_base * 0.004, 2)
    # Invalidez y vida
    invalidez_vida = round(sal_integrado_dia * dias * 0.00625, 2)
    # Cesantía y vejez
    cesantia = round(sal_integrado_dia * dias * 0.01125, 2)
    imss_trabajador = round(cuota_fija + cuota_excedente + invalidez_vida + cesantia, 2)

    # ── IMSS cuotas patronales ──
    em_mat_patron = round(sal_integrado_dia * dias * 0.1005, 2)
    riesgo_trabajo = round(sal_integrado_dia * dias * (e.prima_riesgo_trabajo or 0.005), 2)
    invalidez_patron = round(sal_integrado_dia * dias * 0.01750, 2)
    guarderias = round(sal_integrado_dia * dias * 0.01, 2)
    cesantia_patron = round(sal_integrado_dia * dias * 0.03150, 2)
    imss_patron = round(em_mat_patron + riesgo_trabajo + invalidez_patron + guarderias + cesantia_patron, 2)

    # ── INFONAVIT patronal ──
    infonavit_patron = round(sal_integrado_dia * dias * 0.05, 2)

    # ── INFONAVIT descuento trabajador ──
    infonavit_trabajador = 0.0
    if e.tiene_infonavit and e.descuento_infonavit:
        if e.tipo_descuento_infonavit == "vsm":
            infonavit_trabajador = round(e.descuento_infonavit * SMG_2026, 2)
        elif e.tipo_descuento_infonavit == "porcentaje":
            infonavit_trabajador = round(sal_bruto * e.descuento_infonavit / 100, 2)
        else:
            infonavit_trabajador = e.descuento_infonavit

    # ── ISR ──
    isr = round(_calcular_isr_tabla(sal_bruto), 2)

    # ── Subsidio al empleo ──
    subsidio = _calcular_subsidio_empleo(sal_bruto)

    isr_neto = max(0, isr - subsidio)

    # ── Otras deducciones ──
    caja_ahorro = round(sal_bruto * (e.caja_ahorro_pct or 0) / 100, 2)
    prestamos = e.prestamos or 0.0

    total_deducciones = round(imss_trabajador + isr_neto + infonavit_trabajador + caja_ahorro + prestamos, 2)
    salario_neto = round(sal_bruto - total_deducciones, 2)

    # ── Costo total empresa ──
    costo_empresa = round(sal_bruto + imss_patron + infonavit_patron, 2)

    # ── PTU proporcional ──
    ptu_anual = round(sal_bruto * 12 * 0.10, 2)  # estimado 10% utilidad

    # ── Aguinaldo ──
    aguinaldo_anual = round(e.salario_diario * 15, 2) if e.salario_diario else 0

    # ── Prima vacacional ──
    prima_vacacional = round(e.salario_diario * 6 * 0.25, 2) if e.salario_diario else 0  # 6 días base + 25%

    return {
        "empleado": e.nombre,
        "puesto": e.puesto,
        "periodo_dias": dias,
        "percepciones": {
            "salario_bruto": sal_bruto,
            "percepciones_extra": percepciones_extra,
            "vales_despensa": e.vales_despensa or 0,
            "total": round(sal_bruto + (e.vales_despensa or 0), 2),
        },
        "deducciones_trabajador": {
            "imss": imss_trabajador,
            "isr_causado": isr,
            "subsidio_empleo": subsidio,
            "isr_neto": isr_neto,
            "infonavit_credito": infonavit_trabajador,
            "caja_ahorro": caja_ahorro,
            "prestamos": prestamos,
            "total": total_deducciones,
        },
        "cuotas_patronales": {
            "imss_patron": imss_patron,
            "infonavit_patron": infonavit_patron,
            "total": round(imss_patron + infonavit_patron, 2),
        },
        "salario_neto": salario_neto,
        "costo_total_empresa": costo_empresa,
        "prestaciones_anuales": {
            "aguinaldo": aguinaldo_anual,
            "prima_vacacional": prima_vacacional,
            "ptu_estimado": ptu_anual,
        },
        "info": {
            "uma_2026": UMA_2026,
            "smg_2026": SMG_2026,
            "salario_diario": e.salario_diario,
            "salario_integrado": e.salario_integrado,
            "factor_integracion": e.factor_integracion,
        }
    }


# ═══════════════════════════════════════════════
#  DIRECTORIO — Clientes / Proveedores / Agentes
# ═══════════════════════════════════════════════

@app.post("/contactos", response_model=ContactoResponse, tags=["Directorio"])
async def crear_contacto(
    body: ContactoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contacto = Contacto(tenant_id=current_user.tenant_id, **body.model_dump())
    db.add(contacto)
    db.commit()
    db.refresh(contacto)
    return contacto


@app.get("/contactos", response_model=List[ContactoResponse], tags=["Directorio"])
async def listar_contactos(
    tipo: Optional[str] = None,
    buscar: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Contacto).filter(
        Contacto.tenant_id == current_user.tenant_id,
        Contacto.activo == True,
    )
    if tipo:
        q = q.filter(Contacto.tipo == tipo)
    if buscar:
        term = f"%{buscar}%"
        q = q.filter(
            (Contacto.razon_social.ilike(term)) |
            (Contacto.rfc.ilike(term)) |
            (Contacto.contacto_nombre.ilike(term))
        )
    return q.order_by(Contacto.razon_social).all()


@app.get("/contactos/{contacto_id}", response_model=ContactoResponse, tags=["Directorio"])
async def obtener_contacto(
    contacto_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    c = db.query(Contacto).filter(Contacto.id == contacto_id, Contacto.tenant_id == current_user.tenant_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    # Calcular métricas en tiempo real desde facturas
    from sqlalchemy import func
    ventas = db.query(func.sum(Factura.total), func.count(Factura.id)).filter(
        Factura.tenant_id == current_user.tenant_id,
        Factura.rfc_receptor == c.rfc,
        Factura.tipo == "ingreso",
    ).first()
    compras = db.query(func.sum(Factura.total), func.count(Factura.id)).filter(
        Factura.tenant_id == current_user.tenant_id,
        Factura.rfc_emisor == c.rfc,
        Factura.tipo == "gasto",
    ).first()
    c.monto_total_ventas = float(ventas[0] or 0)
    c.monto_total_compras = float(compras[0] or 0)
    c.total_facturas = int((ventas[1] or 0) + (compras[1] or 0))
    return c


@app.patch("/contactos/{contacto_id}", response_model=ContactoResponse, tags=["Directorio"])
async def actualizar_contacto(
    contacto_id: str,
    body: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    c = db.query(Contacto).filter(Contacto.id == contacto_id, Contacto.tenant_id == current_user.tenant_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    for k, v in body.items():
        if hasattr(c, k):
            setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@app.delete("/contactos/{contacto_id}", tags=["Directorio"])
async def eliminar_contacto(
    contacto_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    c = db.query(Contacto).filter(Contacto.id == contacto_id, Contacto.tenant_id == current_user.tenant_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    c.activo = False
    db.commit()
    return {"ok": True}


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


def _calcular_subsidio_empleo(salario: float) -> float:
    """Subsidio al empleo mensual 2026 (Art. 1 Decreto subsidio)"""
    if salario <= 1768.96:   return 407.02
    elif salario <= 2653.38: return 406.83
    elif salario <= 3472.84: return 406.62
    elif salario <= 3537.87: return 392.77
    elif salario <= 4446.15: return 382.46
    elif salario <= 4717.18: return 354.23
    elif salario <= 5335.42: return 324.87
    elif salario <= 6224.67: return 294.63
    elif salario <= 7113.90: return 253.54
    elif salario <= 7382.33: return 217.61
    else:                    return 0.0


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
        Factura.fecha_emision >= primer_dia,
        Factura.fecha_emision <= ultimo_dia,
    ).all()

    ingresos = sum(f.total for f in facturas if f.tipo == "ingreso")
    gastos = sum(f.total for f in facturas if f.tipo == "gasto")
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
        "isr_estimado": calculos["isr_estimado"],
        "ptu": calculos["ptu_estimada"],
        "ebitda": calculos["ebitda"],
        "margen_neto_pct": calculos["margen_neto_pct"],
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
        getattr(CierreMes, "año") == ano,
        CierreMes.mes == mes,
    ).first()
    if existente and existente.estado == "cerrado":
        raise HTTPException(status_code=400, detail="Cierre ya fue cerrado y no puede modificarse")

    datos = await cierre_mes(ano, mes, current_user, db)

    cierre = existente or CierreMes(tenant_id=current_user.tenant_id, mes=mes)
    setattr(cierre, "año", ano)
    cierre.ingresos_total = datos["ingresos"]
    cierre.egresos_total = datos["gastos"]
    cierre.utilidad_bruta = datos["utilidad_bruta"]
    cierre.iva_cobrado = datos["iva_cobrado"]
    cierre.iva_pagado = datos["iva_pagado"]
    cierre.iva_neto = datos["iva_neto"]
    cierre.isr_estimado = datos["isr_estimado"]
    cierre.resumen_json = datos
    cierre.estado = "cerrado"

    if not existente:
        db.add(cierre)
    db.commit()
    db.refresh(cierre)
    return cierre


@app.post("/cierre/{ano}/{mes}/borrador", response_model=CierreResponse, tags=["Cierre"])
async def guardar_pre_cierre(
    ano: int,
    mes: int,
    current_user: Usuario = Depends(require_role("admin", "contador", "ceo")),
    db: Session = Depends(get_db),
):
    """Guarda un pre-cierre como borrador (puede sobrescribirse hasta que se cierre oficialmente)."""
    existente = db.query(CierreMes).filter(
        CierreMes.tenant_id == current_user.tenant_id,
        getattr(CierreMes, "año") == ano,
        CierreMes.mes == mes,
    ).first()
    if existente and existente.estado == "cerrado":
        raise HTTPException(status_code=400, detail="Ya existe un cierre oficial. No se puede modificar.")

    datos = await cierre_mes(ano, mes, current_user, db)

    cierre = existente or CierreMes(tenant_id=current_user.tenant_id, mes=mes)
    setattr(cierre, "año", ano)
    cierre.ingresos_total = datos["ingresos"]
    cierre.egresos_total = datos["gastos"]
    cierre.utilidad_bruta = datos["utilidad_bruta"]
    cierre.iva_cobrado = datos["iva_cobrado"]
    cierre.iva_pagado = datos["iva_pagado"]
    cierre.iva_neto = datos["iva_neto"]
    cierre.isr_estimado = datos["isr_estimado"]
    cierre.resumen_json = datos
    cierre.estado = "borrador"

    if not existente:
        db.add(cierre)
    db.commit()
    db.refresh(cierre)
    return cierre


@app.get("/cierre/{ano}/{mes}/estado", tags=["Cierre"])
async def cierre_estado(
    ano: int,
    mes: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve si hay un cierre guardado para el periodo y su estado."""
    registro = db.query(CierreMes).filter(
        CierreMes.tenant_id == current_user.tenant_id,
        getattr(CierreMes, "año") == ano,
        CierreMes.mes == mes,
    ).first()
    if not registro:
        return {"estado": "sin_registro", "periodo": f"{ano}-{mes:02d}"}
    return {
        "estado": registro.estado,
        "periodo": f"{ano}-{mes:02d}",
        "id": registro.id,
        "ingresos_total": registro.ingresos_total,
        "egresos_total": registro.egresos_total,
        "utilidad_bruta": registro.utilidad_bruta,
        "iva_neto": registro.iva_neto,
        "isr_estimado": registro.isr_estimado,
        "created_at": str(registro.created_at),
    }


# ═══════════════════════════════════════════════
#  DASHBOARD EJECUTIVO
# ═══════════════════════════════════════════════

@app.get("/dashboard", response_model=DashboardResponse, tags=["Dashboard"])
async def dashboard(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import timezone as _tz
    ahora = datetime.now(_tz.utc)
    inicio_mes = datetime(ahora.year, ahora.month, 1, tzinfo=_tz.utc)

    facturas = db.query(Factura).filter(Factura.tenant_id == current_user.tenant_id).all()
    mes_actual = [f for f in facturas if f.fecha_emision and f.fecha_emision.replace(tzinfo=_tz.utc) >= inicio_mes]

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
    """
    Parsea CFDI 4.0 y 3.3. Extrae:
    - Campos base: emisor, receptor, subtotal, total, moneda, UUID
    - IVA trasladado (16%) desde nodo Traslados
    - Retenciones: ISR (001) y IVA (002) — clave para RESICO 1.25%
    - RegimenFiscal del Emisor (621=RESICO PF, 626=RESICO PM, 601=General)
    - Tipo de comprobante: I=ingreso, E=egreso, N=nómina
    """
    root = ET.fromstring(xml_bytes)
    ns = "cfdi" if root.tag.startswith("{http://www.sat.gob.mx/cfd/4}") else "cfdi3"

    def attr(node, name, default=""):
        return (node.get(name) or default) if node is not None else default

    subtotal = float(attr(root, "SubTotal", "0") or "0")
    total = float(attr(root, "Total", "0") or "0")
    moneda = attr(root, "Moneda", "MXN")
    tipo_cambio = float(attr(root, "TipoCambio", "1") or "1")
    tipo_comprobante = attr(root, "TipoDeComprobante", "I")
    uuid_cfdi = ""
    fecha_str = attr(root, "Fecha", "")

    # UUID del timbre
    for comp in root.iter():
        if "TimbreFiscalDigital" in comp.tag:
            uuid_cfdi = comp.get("UUID", "")
            break

    # Emisor y Receptor
    emisor = (root.find(".//{http://www.sat.gob.mx/cfd/4}Emisor")
              or root.find(".//{http://www.sat.gob.mx/cfd/3}Emisor"))
    receptor = (root.find(".//{http://www.sat.gob.mx/cfd/4}Receptor")
                or root.find(".//{http://www.sat.gob.mx/cfd/3}Receptor"))

    rfc_emisor = attr(emisor, "Rfc")
    nombre_emisor = attr(emisor, "Nombre")
    rfc_receptor = attr(receptor, "Rfc")
    nombre_receptor = attr(receptor, "Nombre")
    # RegimenFiscal: 621=RESICO PF, 626=RESICO PM, 601=General, 612=Honorarios
    regimen_emisor = attr(emisor, "RegimenFiscal", "601")

    # Conceptos (descripción del primer concepto)
    conceptos = [c.get("Descripcion", "") for c in root.iter()
                 if "Concepto" in c.tag and "Conceptos" not in c.tag]
    concepto = (conceptos[0] if conceptos else "CFDI importado")[:500]

    # IVA trasladado 16% desde nodo Traslado
    iva = 0.0
    for t in root.iter():
        if "Traslado" in t.tag and "Retenciones" not in (t.tag or ""):
            tasa = float(t.get("TasaOCuota", "0") or "0")
            if abs(tasa - 0.16) < 0.001:
                importe = t.get("Importe")
                if importe:
                    iva = round(float(importe), 2)
                else:
                    base = float(t.get("Base", subtotal) or subtotal)
                    iva = round(base * 0.16, 2)
                break

    # Retenciones: ISR (001) y IVA (002)
    # ISR retenido 1.25% → aplica en RESICO PF cuando cobra a PM
    isr_retenido = 0.0
    iva_retenido = 0.0
    for ret in root.iter():
        if "Retencion" in ret.tag and "Retenciones" not in ret.tag:
            impuesto = ret.get("Impuesto", "")
            importe = float(ret.get("Importe", "0") or "0")
            if impuesto == "001":  # ISR
                isr_retenido = round(importe, 2)
            elif impuesto == "002":  # IVA
                iva_retenido = round(importe, 2)

    # Determinar tipo: I=ingreso, E/N/P=gasto
    tipo = "ingreso" if tipo_comprobante == "I" else "gasto"

    # Determinar régimen fiscal del emisor
    REGIMENES = {
        "621": "resico_pf",
        "626": "resico_pm",
        "601": "general",
        "612": "honorarios",
        "616": "sin_obligaciones",
        "625": "coordinados",
    }
    regimen = REGIMENES.get(regimen_emisor, f"otro_{regimen_emisor}")

    fecha = None
    try:
        if fecha_str:
            fecha = datetime.fromisoformat(fecha_str.replace("T", " ").split(".")[0])
    except Exception:
        pass

    return {
        "rfc_emisor": rfc_emisor,
        "nombre_emisor": nombre_emisor,
        "rfc_receptor": rfc_receptor,
        "nombre_receptor": nombre_receptor,
        "subtotal": subtotal,
        "iva": iva,
        "isr_retenido": isr_retenido,
        "iva_retenido": iva_retenido,
        "total": total,
        "moneda": moneda,
        "tipo_cambio": tipo_cambio,
        "concepto": concepto,
        "uuid_cfdi": uuid_cfdi,
        "tipo": tipo,
        "fecha": fecha,
        "regimen_fiscal": regimen,
        "regimen_codigo": regimen_emisor,
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

    total_calc = datos["subtotal"] + datos["iva"]

    factura = Factura(
        tenant_id=current_user.tenant_id,
        rfc_emisor=datos["rfc_emisor"],
        nombre_emisor=datos["nombre_emisor"],
        rfc_receptor=datos["rfc_receptor"],
        nombre_receptor=datos.get("nombre_receptor", ""),
        subtotal=datos["subtotal"],
        iva=datos["iva"],
        isr_retenido=datos["isr_retenido"],
        iva_retenido=datos["iva_retenido"],
        total=total_calc,
        tipo=datos["tipo"],
        moneda=datos["moneda"],
        tipo_cambio=datos["tipo_cambio"],
        concepto=datos["concepto"],
        uuid_cfdi=datos["uuid_cfdi"] or None,
        fecha_emision=datos["fecha"] or datetime.utcnow(),
        regimen_fiscal=datos["regimen_fiscal"],
        tipo_pago="pendiente",
        estado="pendiente",
        xml_cfdi=xml_bytes.decode("utf-8", errors="ignore")[:50000],
    )
    db.add(factura)
    _audit(db, "cargar_cfdi_xml", current_user, "facturas", {
        "uuid": datos["uuid_cfdi"], "total": total_calc,
        "isr_retenido": datos["isr_retenido"], "regimen": datos["regimen_fiscal"]
    })
    db.commit()
    db.refresh(factura)

    if REDIS_OK:
        mes_key = f"cierre:{current_user.tenant_id}:{factura.fecha_emision.year}:{factura.fecha_emision.month}"
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
    semaforo: Optional[str] = None
    semaforo_errores: Optional[list] = None
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


@app.post("/mve/{mve_id}/validar", tags=["MVE"])
async def validar_mve_endpoint(
    mve_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Valida la MVE contra RGCE y Ley Aduanera. Devuelve semáforo rojo/amarillo/verde."""
    from models import MVE as MVEModel
    from mve_validator import validar_mve
    mve = db.query(MVEModel).filter(
        MVEModel.id == mve_id, MVEModel.tenant_id == str(current_user.tenant_id)
    ).first()
    if not mve:
        raise HTTPException(404, "MVE no encontrada")
    resultado = validar_mve(mve)
    mve.semaforo = resultado["semaforo"]
    mve.semaforo_errores = resultado["errores"]
    mve.semaforo_validado_at = datetime.utcnow()
    if resultado["puede_presentar"] and mve.estado == "borrador":
        mve.estado = "lista"
    db.commit()
    return resultado


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
_sys.path.insert(0, str(_APP / "app" / "ai"))  # expone orchestrator/, memory/, agents/, skills/

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
        _configs = _APP / "app" / "ai" / "configs"
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
# BRAIN — RAG + Ollama local (phi3-fast) + caché Redis
# Arquitectura: Redis Cache → Qdrant semántico → PostgreSQL full-text → Ollama+contexto → respuesta
# ══════════════════════════════════════════════════════════════════════════════

import hashlib as _hashlib
import urllib.request as _urllib_req
import json as _json

_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
_BRAIN_CACHE_TTL = int(os.environ.get("BRAIN_CACHE_TTL", "3600"))

# Qdrant RAG — importación con fallback si el servicio no está disponible aún
try:
    from app.ai.memory.qdrant_rag import QdrantRAG as _QdrantRAG
    _qdrant_rag = _QdrantRAG()
    _QDRANT_ENABLED = True
except Exception:
    _qdrant_rag = None
    _QDRANT_ENABLED = False

# Queen-Worker Swarm — importación con fallback
try:
    from app.ai.swarm.queen import queen as _queen
    _SWARM_ENABLED = True
except Exception:
    _queen = None
    _SWARM_ENABLED = False

# Mapeo context → colección Qdrant
_CONTEXT_COLLECTION = {
    "default": "fiscal_mx",
    "fiscal": "fiscal_mx",
    "fiscal_mx": "fiscal_mx",
    "fourgea": "fourgea_docs",
    "tripler": "tripler_docs",
}

_BRAIN_SYSTEM = (
    "Eres Mystic, el asistente fiscal y contable de Sonora Digital Corp. "
    "Respondes preguntas sobre contabilidad, fiscalidad mexicana e importaciones. "
    "REGLA CRÍTICA: usa SOLO los datos de la BASE DE CONOCIMIENTO proporcionada. "
    "Si la respuesta está en el contexto, cítala con precisión (cifras, artículos, fechas). "
    "Si NO está en el contexto, di exactamente: 'No tengo información verificada sobre esto.' "
    "NO inventes cifras, tasas, artículos de ley ni fechas. "
    "Responde siempre en español, de forma concisa y estructurada."
)


class _BrainRequest(BaseModel):
    question: str
    context: str = "default"
    use_cache: bool = True
    session_id: Optional[str] = None   # P2: memoria cross-session
    channel: str = "api"               # whatsapp | telegram | dashboard | api


class _BrainResponse(BaseModel):
    answer: str
    source: str        # "cache" | "qdrant+ollama" | "qdrant_direct" | "rag+ollama" | "rag_direct"
    model: str = "deepseek-r1:1.5b"
    cached: bool = False
    chunks_used: int = 0
    qdrant_used: bool = False
    session_id: Optional[str] = None
    agents_used: Optional[list] = None  # P1: swarm


class _SwarmRequest(BaseModel):
    question: str
    context: str = "default"
    session_id: Optional[str] = None
    channel: str = "api"


class _SwarmResponse(BaseModel):
    answer: str
    agents_used: list[str]
    confidences: dict
    total_chunks: int
    session_id: Optional[str] = None
    source: str = "swarm"


class _FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: int          # +1 buena | -1 mala
    context: str = "fiscal"
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None


def _redis_client():
    return redis.from_url(os.environ.get("REDIS_URL", "redis://redis:6379/0"), decode_responses=True)


def _cache_key(question: str, context: str) -> str:
    return "brain:" + _hashlib.md5(f"{context}:{question.strip().lower()}".encode()).hexdigest()


# ── RAG: busca chunks relevantes en knowledge_base ────────────────────────────
def _rag_search(db: Session, question: str, limit: int = 4) -> list[dict]:
    """Full-text search en knowledge_base usando tsvector de PostgreSQL."""
    try:
        # Limpiar pregunta para tsquery — palabras significativas (>2 para capturar IVA, DTA, IGI)
        words = [w for w in question.replace("?","").replace(",","").split() if len(w) > 2]
        if not words:
            return []
        tsquery = " | ".join(words[:8])  # OR entre palabras clave
        rows = db.execute(text("""
            SELECT title, content, source, topic,
                   ts_rank(to_tsvector('spanish', title||' '||content||' '||COALESCE(keywords,'')),
                           to_tsquery('spanish', :q)) AS rank
            FROM knowledge_base
            WHERE to_tsvector('spanish', title||' '||content||' '||COALESCE(keywords,''))
                  @@ to_tsquery('spanish', :q)
            ORDER BY rank DESC
            LIMIT :limit
        """), {"q": tsquery, "limit": limit}).fetchall()

        # Fallback: ILIKE si tsquery no da resultados
        if not rows:
            pattern = f"%{words[0]}%"
            rows = db.execute(text("""
                SELECT title, content, source, topic, 0.1 AS rank
                FROM knowledge_base
                WHERE content ILIKE :p OR title ILIKE :p OR keywords ILIKE :p
                LIMIT :limit
            """), {"p": pattern, "limit": limit}).fetchall()

        return [{"title": r[0], "content": r[1], "source": r[2], "topic": r[3]} for r in rows]
    except Exception:
        return []


async def _rag_search_qdrant(question: str, context: str, limit: int = 3) -> list[dict]:
    """Búsqueda semántica en Qdrant. Devuelve lista compatible con _rag_search."""
    if not _QDRANT_ENABLED or _qdrant_rag is None:
        return []
    try:
        collection = _CONTEXT_COLLECTION.get(context, "fiscal_mx")
        results = await _qdrant_rag.search(collection, question, limit=limit, score_threshold=0.45)
        return [
            {
                "title": r.get("title", r.get("doc_id", "Documento")),
                "content": r["text"],
                "source": r.get("fuente", "qdrant"),
                "topic": r.get("topic", context),
            }
            for r in results
        ]
    except Exception:
        return []


_MAX_CHUNK_CHARS = 300   # truncar chunks para no saturar contexto phi3-fast (6.6 t/s)
_RAG_LIMIT = 2           # máximo 2 chunks por consulta

# Sistema compacto para minimizar tokens de entrada
_BRAIN_SYSTEM_SHORT = (
    "Eres Mystic, asistente fiscal mexicano. "
    "Usa SOLO los datos del contexto dado. "
    "Si no está en el contexto, di: 'No tengo información verificada.' "
    "Sé conciso. No inventes cifras ni artículos."
)

_DIRECT_KEYWORDS = {
    "iva", "tasa", "porcentaje", "cuánto", "cuando", "plazo", "fecha",
    "artículo", "fracción", "igi", "dta", "imss", "rfc", "cfdi", "timbrar",
}


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        content = c['content']
        if len(content) > _MAX_CHUNK_CHARS:
            content = content[:_MAX_CHUNK_CHARS] + "…"
        parts.append(f"[{i}. {c['title']}]\n{content}")
    return "\n\n".join(parts)


def _is_direct_lookup(question: str, chunks: list[dict]) -> bool:
    """Detecta si la pregunta es un lookup simple que el RAG puede responder directamente."""
    if not chunks:
        return False
    q_lower = question.lower()
    # Whole-word matching para evitar falsos positivos ("definitiva" no es "iva")
    kw_hit = any(_re.search(r'\b' + k + r'\b', q_lower) for k in _DIRECT_KEYWORDS)
    # Si el título del primer chunk aparece parcialmente en la pregunta
    title_words = {w for w in chunks[0]['title'].lower().split() if len(w) > 3}
    q_words = set(q_lower.split())
    title_hit = len(title_words & q_words) >= 2
    return kw_hit or title_hit


_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "deepseek-r1:1.5b")
_OLLAMA_FALLBACK = "phi3-fast"  # fallback si deepseek no está disponible

import re as _re

def _strip_think_tags(text: str) -> str:
    """Elimina bloques <think>...</think> que genera DeepSeek-R1 (razonamiento interno)."""
    return _re.sub(r"<think>.*?</think>", "", text, flags=_re.DOTALL).strip()


def _ollama_ask(question: str, rag_context: str) -> str:
    system = _BRAIN_SYSTEM_SHORT
    if rag_context:
        system += f"\n\nCONTEXTO:\n{rag_context}"

    # DeepSeek-R1 necesita más tokens (genera razonamiento + respuesta)
    is_deepseek = "deepseek" in _OLLAMA_MODEL
    num_predict = 400 if is_deepseek else 150
    num_ctx = 2048 if is_deepseek else 512

    payload = _json.dumps({
        "model": _OLLAMA_MODEL,
        "prompt": f"Responde brevemente en español: {question}",
        "system": system,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": num_predict, "num_ctx": num_ctx},
    }).encode()
    req = _urllib_req.Request(
        f"{_OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with _urllib_req.urlopen(req, timeout=60) as r:
        raw = _json.loads(r.read()).get("response", "").strip()
    return _strip_think_tags(raw) if is_deepseek else raw


# ── P1: RAG por colección específica (para los workers del swarm) ─────────────
async def _rag_search_by_collection(question: str, collection: str, limit: int = 2) -> list[dict]:
    """Búsqueda en una colección Qdrant específica (usada por Queen workers)."""
    if not _QDRANT_ENABLED or _qdrant_rag is None:
        return []
    try:
        results = await _qdrant_rag.search(collection, question, limit=limit, score_threshold=0.4)
        return [
            {
                "title": r.get("title", r.get("doc_id", "Documento")),
                "content": r["text"],
                "source": r.get("fuente", "qdrant"),
                "topic": r.get("topic", collection),
            }
            for r in results
        ]
    except Exception:
        return []


# ── P2: Helpers de memoria cross-session ─────────────────────────────────────
_SESSION_MAX_MSGS = 10   # Máximo mensajes a retener por sesión


def _session_get(db: Session, session_id: str) -> BrainSession | None:
    return db.query(BrainSession).filter(BrainSession.session_id == session_id).first()


def _session_save(db: Session, session_id: str, channel: str,
                  question: str, answer: str, tenant_id: str | None = None) -> None:
    """Añade el par Q/A a la sesión, creándola si no existe. Mantiene últimos N mensajes."""
    import datetime as _dt
    now_str = _dt.datetime.now(_dt.timezone.utc).isoformat()
    sess = _session_get(db, session_id)
    if sess is None:
        sess = BrainSession(
            session_id=session_id,
            channel=channel,
            tenant_id=tenant_id,
            messages=[],
        )
        db.add(sess)

    msgs: list = list(sess.messages or [])
    msgs.append({"role": "user", "content": question, "ts": now_str})
    msgs.append({"role": "assistant", "content": answer, "ts": now_str})
    # Mantener solo los últimos _SESSION_MAX_MSGS mensajes
    sess.messages = msgs[-_SESSION_MAX_MSGS:]
    try:
        db.commit()
    except Exception:
        db.rollback()


def _session_history_text(db: Session, session_id: str | None) -> str:
    """Devuelve texto con los últimos 5 intercambios para inyectar como contexto."""
    if not session_id:
        return ""
    sess = _session_get(db, session_id)
    if not sess or not sess.messages:
        return ""
    # Últimos 5 mensajes (puede ser 2-3 intercambios)
    recent = sess.messages[-5:]
    lines = []
    for m in recent:
        prefix = "Usuario" if m.get("role") == "user" else "Mystic"
        lines.append(f"{prefix}: {m['content'][:200]}")
    return "\n".join(lines)


@app.post("/api/brain/ask", response_model=_BrainResponse, tags=["Brain"])
async def brain_ask(body: _BrainRequest, db: Session = Depends(get_db)):
    """
    Brain RAG: busca en knowledge_base fiscal → Ollama con contexto verificado.
    Respuestas precisas sin alucinaciones sobre tasas, artículos y trámites mexicanos.
    """
    key = _cache_key(body.question, body.context)

    # Capa 1: Redis Cache
    if body.use_cache:
        try:
            cached = _redis_client().get(key)
            if cached:
                d = _json.loads(cached)
                return _BrainResponse(**d, cached=True)
        except Exception:
            pass

    # Capa 2: Qdrant semántico (prioritario) → fallback PostgreSQL full-text
    qdrant_chunks = await _rag_search_qdrant(body.question, body.context, limit=_RAG_LIMIT)
    if qdrant_chunks:
        chunks = qdrant_chunks
        qdrant_used = True
    else:
        chunks = _rag_search(db, body.question, limit=_RAG_LIMIT)
        qdrant_used = False
    rag_ctx = _build_context(chunks)

    # Capa 2.5: Direct RAG — para lookups simples, responde directamente sin Ollama
    if chunks and _is_direct_lookup(body.question, chunks):
        top = chunks[0]['content']
        lines = [l.strip() for l in top.split('\n') if l.strip()][:4]
        answer = '\n'.join(lines)
        if chunks[0].get('source'):
            answer += f"\n[Fuente: {chunks[0]['source']}]"
        result = _BrainResponse(
            answer=answer,
            source="qdrant_direct" if qdrant_used else "rag_direct",
            cached=False,
            chunks_used=len(chunks),
            qdrant_used=qdrant_used,
            session_id=body.session_id,
        )
        if body.use_cache:
            try:
                _redis_client().setex(key, _BRAIN_CACHE_TTL, _json.dumps(result.model_dump()))
            except Exception:
                pass
        if body.session_id:
            try:
                _session_save(db, body.session_id, body.channel, body.question, answer)
            except Exception:
                pass
        return result

    # P2: Inyectar historial de sesión al contexto RAG
    history_ctx = _session_history_text(db, body.session_id)
    if history_ctx:
        rag_ctx = f"CONVERSACIÓN PREVIA:\n{history_ctx}\n\nCONOCIMIENTO:\n{rag_ctx}" if rag_ctx else f"CONVERSACIÓN PREVIA:\n{history_ctx}"

    # Capa 3: Ollama con contexto RAG (síntesis para preguntas complejas)
    try:
        answer = _ollama_ask(body.question, rag_ctx)
        result = _BrainResponse(
            answer=answer,
            source="qdrant+ollama" if qdrant_used else "rag+ollama",
            cached=False,
            chunks_used=len(chunks),
            qdrant_used=qdrant_used,
            session_id=body.session_id,
        )
        if body.use_cache:
            try:
                _redis_client().setex(key, _BRAIN_CACHE_TTL, _json.dumps(result.model_dump()))
            except Exception:
                pass
        # P2: Guardar en sesión (no bloqueante)
        if body.session_id:
            try:
                _session_save(db, body.session_id, body.channel, body.question, answer)
            except Exception:
                pass
        return result
    except Exception as e:
        # Fallback: si Ollama falla, devolver el RAG directo
        if chunks:
            top = chunks[0]['content']
            lines = [l.strip() for l in top.split('\n') if l.strip()][:4]
            answer = '\n'.join(lines)
            if chunks[0].get('source'):
                answer += f"\n[Fuente: {chunks[0]['source']}]"
            result = _BrainResponse(
                answer=answer,
                source="qdrant_fallback" if qdrant_used else "rag_fallback",
                cached=False,
                chunks_used=len(chunks),
                qdrant_used=qdrant_used,
                session_id=body.session_id,
            )
            if body.use_cache:
                try:
                    _redis_client().setex(key, _BRAIN_CACHE_TTL, _json.dumps(result.model_dump()))
                except Exception:
                    pass
            return result
        raise HTTPException(status_code=503, detail=f"Brain no disponible: {str(e)}")


@app.get("/api/brain/status", tags=["Brain"])
async def brain_status(db: Session = Depends(get_db)):
    """Estado del Brain: Ollama + knowledge_base."""
    try:
        req = _urllib_req.Request(f"{_OLLAMA_URL}/api/tags")
        with _urllib_req.urlopen(req, timeout=5) as r:
            models = [m["name"] for m in _json.loads(r.read()).get("models", [])]
        ollama_ok = True
    except Exception as e:
        models, ollama_ok = [], False

    try:
        kb_count = db.execute(text("SELECT COUNT(*) FROM knowledge_base")).scalar()
        topics = dict(db.execute(text(
            "SELECT topic, COUNT(*) FROM knowledge_base GROUP BY topic ORDER BY topic"
        )).fetchall())
    except Exception:
        kb_count, topics = 0, {}

    # Estado Qdrant
    qdrant_status = {"enabled": _QDRANT_ENABLED, "collections": []}
    if _QDRANT_ENABLED and _qdrant_rag is not None:
        try:
            cols = await _qdrant_rag._client.get_collections()
            qdrant_status["collections"] = [
                {"name": c.name, "status": "ok"} for c in cols.collections
            ]
            qdrant_status["status"] = "ok"
        except Exception:
            qdrant_status["status"] = "error"
    else:
        qdrant_status["status"] = "disabled"

    return {
        "ollama": "ok" if ollama_ok else "error",
        "models": models,
        "phi3_ready": any("phi3" in m for m in models),
        "active_model": _OLLAMA_MODEL,
        "deepseek_ready": any("deepseek-r1" in m for m in models),
        "knowledge_base": {"total": kb_count, "topics": topics},
        "qdrant": qdrant_status,
    }


# ── P1: Queen-Worker Swarm ────────────────────────────────────────────────────

@app.post("/api/brain/swarm", response_model=_SwarmResponse, tags=["Brain"])
async def brain_swarm(body: _SwarmRequest, db: Session = Depends(get_db)):
    """
    Queen-Worker Swarm: despacha pregunta a 3 agentes especializados en paralelo
    (AgentFacturas, AgentNomina, AgentIVA) y consolida respuestas por confianza.
    Ideal para consultas fiscales complejas multi-dominio.
    """
    if not _SWARM_ENABLED or _queen is None:
        raise HTTPException(503, "Swarm no disponible — queen.py no cargó correctamente")

    # P2: Historial de sesión como prefijo de pregunta
    history_ctx = _session_history_text(db, body.session_id)
    question_with_ctx = body.question
    if history_ctx:
        question_with_ctx = f"Contexto conversación:\n{history_ctx}\n\nPregunta: {body.question}"

    result = await _queen.run(question_with_ctx, _rag_search_by_collection, _ollama_ask)

    # P2: Guardar en sesión
    if body.session_id and result.get("answer"):
        try:
            _session_save(db, body.session_id, body.channel, body.question, result["answer"])
        except Exception:
            pass

    return _SwarmResponse(
        answer=result["answer"],
        agents_used=result.get("agents_used", []),
        confidences=result.get("confidences", {}),
        total_chunks=result.get("total_chunks", 0),
        session_id=body.session_id,
    )


# ── P3: Feedback y auto-aprendizaje ──────────────────────────────────────────

@app.post("/api/brain/feedback", tags=["Brain"])
async def brain_feedback(body: _FeedbackRequest, db: Session = Depends(get_db)):
    """
    Registra feedback del usuario (+1 buena / -1 mala).
    Si rating=+1, re-indexa el Q&A en Qdrant como nuevo conocimiento verificado.
    """
    fb = BrainFeedback(
        session_id=body.session_id,
        tenant_id=body.tenant_id,
        question=body.question,
        answer=body.answer,
        rating=body.rating,
        context=body.context,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    # Re-indexar en Qdrant si es respuesta buena y Qdrant está disponible
    indexed = False
    if body.rating == 1 and _QDRANT_ENABLED and _qdrant_rag is not None:
        try:
            collection = _CONTEXT_COLLECTION.get(body.context, "fiscal_mx")
            doc_text = f"Pregunta: {body.question}\nRespuesta verificada: {body.answer}"
            await _qdrant_rag.upsert(
                collection,
                f"feedback_{fb.id}",
                doc_text,
                {"source": "user_feedback", "context": body.context, "rating": 1},
            )
            fb.indexed_qdrant = True
            db.commit()
            indexed = True
        except Exception:
            pass

    return {"ok": True, "id": fb.id, "rating": body.rating, "indexed_qdrant": indexed}


# ── Indexación en Qdrant ───────────────────────────────────────────────────────

class _IndexRequest(BaseModel):
    doc_id: str
    text: str
    context: str = "default"
    metadata: dict = {}


class _IndexBatchRequest(BaseModel):
    docs: List[dict]  # [{id, text, metadata?}]
    context: str = "default"


@app.post("/api/brain/index", tags=["Brain"])
async def brain_index(body: _IndexRequest, current_user=Depends(get_current_user)):
    """Indexa un documento en Qdrant para búsqueda semántica."""
    if not _QDRANT_ENABLED or _qdrant_rag is None:
        raise HTTPException(503, "Qdrant no disponible")
    collection = _CONTEXT_COLLECTION.get(body.context, "fiscal_mx")
    await _qdrant_rag.upsert(collection, body.doc_id, body.text, body.metadata)
    return {"ok": True, "collection": collection, "doc_id": body.doc_id}


@app.post("/api/brain/index/batch", tags=["Brain"])
async def brain_index_batch(body: _IndexBatchRequest, current_user=Depends(get_current_user)):
    """Indexa múltiples documentos en Qdrant en un solo request."""
    if not _QDRANT_ENABLED or _qdrant_rag is None:
        raise HTTPException(503, "Qdrant no disponible")
    collection = _CONTEXT_COLLECTION.get(body.context, "fiscal_mx")
    await _qdrant_rag.upsert_batch(collection, body.docs)
    return {"ok": True, "collection": collection, "indexed": len(body.docs)}


# ── WHATSAPP WEBHOOK ──────────────────────────────────────────────────────────

class _WAWebhook(BaseModel):
    from_: str = ""
    message: str = ""
    timestamp: Optional[int] = None

    model_config = {"populate_by_name": True}

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if isinstance(obj, dict) and "from" in obj:
            obj = dict(obj)
            obj["from_"] = obj.pop("from")
        return super().model_validate(obj, *args, **kwargs)


_WA_API_KEY = os.getenv("WA_API_KEY", "MysticWA2026!")
_WA_URL = os.getenv("WA_URL", "http://whatsapp:3001")


async def _wa_send(to: str, message: str) -> bool:
    """Envía mensaje WhatsApp vía mystic-wa."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=15) as http:
            r = await http.post(
                f"{_WA_URL}/send",
                json={"to": to, "message": message},
                headers={"x-api-key": _WA_API_KEY},
            )
            return r.status_code == 200
    except Exception:
        return False


# Números autorizados a usar Mystic por WhatsApp (whitelist)
# Vacío = todos los contactos responden (modo demo)
# Agregar números sin +52, ej: "6622681111", "6623538272"
_WA_WHITELIST: set[str] = set(
    n.strip() for n in os.getenv("WA_WHITELIST", "6622681111,6623538272").split(",") if n.strip()
)

# Grupos siempre ignorados (JIDs con @g.us)
_WA_IGNORE_GROUPS = True

# Respuesta cuando el brain devuelve texto vacío (DeepSeek sin respuesta visible)
_WA_FALLBACK = (
    "Hola, soy Mystic 🤖 Tu asistente fiscal. "
    "Recibí tu pregunta pero necesito más contexto o no encontré información verificada al respecto. "
    "¿Puedes ser más específico?"
)


@app.post("/api/wa/webhook", tags=["WhatsApp"])
async def wa_webhook(body: dict, db: Session = Depends(get_db)):
    """
    Recibe mensajes de WhatsApp desde mystic-wa y responde con el Brain.
    Solo responde a números en WA_WHITELIST. Ignora grupos.
    """
    from_number = body.get("from", "")
    message = body.get("message", "").strip()
    if not from_number or not message:
        return {"ok": False}

    # Ignorar grupos (@g.us) y lids (@lid son notificaciones de sistema)
    if _WA_IGNORE_GROUPS and ("@g.us" in from_number or "@lid" in from_number):
        return {"ok": False, "reason": "group_ignored"}

    # Limpiar número para comparar (quitar 521 o 52 del prefijo internacional)
    clean_number = from_number.replace("521", "", 1).replace("52", "", 1) if from_number.startswith("52") else from_number
    # También intentar match directo
    if _WA_WHITELIST and clean_number not in _WA_WHITELIST and from_number not in _WA_WHITELIST:
        return {"ok": False, "reason": "not_whitelisted"}

    # Detectar contexto por número conocido
    # Nathaly (Fourgea): 6622681111
    fourgea_numbers = {"6622681111"}
    context = "fourgea" if clean_number in fourgea_numbers else "fiscal"

    # P2: session_id por número WhatsApp para memoria cross-session
    session_id = f"whatsapp:{clean_number}"

    # Llamar al Brain con memoria de sesión
    brain_body = _BrainRequest(
        question=message, context=context, use_cache=True,
        session_id=session_id, channel="whatsapp",
    )
    try:
        resp = await brain_ask(brain_body, db)
        answer = resp.answer.strip()
    except Exception as e:
        answer = ""

    # Fallback si la respuesta quedó vacía (DeepSeek sin texto visible)
    if not answer or len(answer) < 5:
        answer = _WA_FALLBACK

    # Responder por WhatsApp
    await _wa_send(from_number, answer)
    return {"ok": True, "answered": answer[:100]}


@app.get("/api/wa/status", tags=["WhatsApp"])
async def wa_status():
    """Estado de la conexión WhatsApp."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=5) as http:
            r = await http.get(
                f"{_WA_URL}/status",
                headers={"x-api-key": _WA_API_KEY},
            )
            return r.json()
    except Exception as e:
        return {"state": "unreachable", "error": str(e)}


# ═══════════════════════════════════════════════
#  RESICO — REPORTES FISCALES
# ═══════════════════════════════════════════════

@app.patch("/facturas/{factura_id}/tipo-pago", tags=["Facturas"])
async def actualizar_tipo_pago(
    factura_id: str,
    body: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza el estado de pago de una factura: prepagado | pendiente | pagado | cancelado."""
    factura = db.query(Factura).filter(
        Factura.id == factura_id,
        Factura.tenant_id == current_user.tenant_id,
    ).first()
    if not factura:
        raise HTTPException(404, "Factura no encontrada")

    tipo_pago = body.get("tipo_pago", "pendiente")
    if tipo_pago not in ("prepagado", "pendiente", "pagado", "cancelado"):
        raise HTTPException(400, "tipo_pago inválido. Usa: prepagado, pendiente, pagado, cancelado")

    factura.tipo_pago = tipo_pago
    if tipo_pago == "pagado":
        factura.estado = "pagada"
        factura.fecha_pago = datetime.utcnow()
    elif tipo_pago == "cancelado":
        factura.estado = "cancelada"

    db.commit()
    return {"ok": True, "factura_id": factura_id, "tipo_pago": tipo_pago}


@app.get("/resico/reporte-iva/{ano}/{mes}", tags=["RESICO"])
async def resico_reporte_iva(
    ano: int,
    mes: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reporte IVA mensual (aplica a cualquier régimen):
    - IVA cobrado = suma IVA de facturas de INGRESO
    - IVA acreditable = suma IVA de facturas de EGRESO (gastos deducibles con CFDI)
    - IVA retenido cobrado = IVA que retuvieron al emisor (ingresos)
    - IVA neto a pagar al SAT = cobrado - acreditable - retenido_a_favor
    """
    primer_dia = datetime(ano, mes, 1)
    ultimo_dia = datetime(ano, mes, calendar.monthrange(ano, mes)[1], 23, 59, 59)

    facturas = db.query(Factura).filter(
        Factura.tenant_id == current_user.tenant_id,
        Factura.fecha_emision >= primer_dia,
        Factura.fecha_emision <= ultimo_dia,
        Factura.estado != "cancelada",
    ).all()

    ingresos = [f for f in facturas if f.tipo == "ingreso"]
    egresos = [f for f in facturas if f.tipo == "gasto"]

    iva_cobrado = round(sum(f.iva or 0 for f in ingresos), 2)
    iva_acreditable = round(sum(f.iva or 0 for f in egresos), 2)
    iva_retenido_ingresos = round(sum(getattr(f, "iva_retenido", 0) or 0 for f in ingresos), 2)
    iva_neto = round(iva_cobrado - iva_acreditable - iva_retenido_ingresos, 2)

    detalle_ingresos = [{
        "folio": f.folio, "uuid": f.uuid_cfdi, "rfc_receptor": f.rfc_receptor,
        "nombre_receptor": getattr(f, "nombre_receptor", ""),
        "subtotal": f.subtotal, "iva": f.iva,
        "iva_retenido": getattr(f, "iva_retenido", 0) or 0,
        "total": f.total, "fecha": str(f.fecha_emision)[:10],
        "tipo_pago": getattr(f, "tipo_pago", "pendiente") or "pendiente",
        "concepto": (f.concepto or "")[:60],
    } for f in ingresos]

    detalle_egresos = [{
        "folio": f.folio, "uuid": f.uuid_cfdi, "rfc_emisor": f.rfc_emisor,
        "nombre_emisor": getattr(f, "nombre_emisor", ""),
        "subtotal": f.subtotal, "iva": f.iva,
        "total": f.total, "fecha": str(f.fecha_emision)[:10],
        "tipo_pago": getattr(f, "tipo_pago", "pendiente") or "pendiente",
        "concepto": (f.concepto or "")[:60],
    } for f in egresos]

    return {
        "periodo": f"{ano}-{mes:02d}",
        "tenant_id": current_user.tenant_id,
        "resumen": {
            "iva_cobrado": iva_cobrado,
            "iva_acreditable": iva_acreditable,
            "iva_retenido_a_favor": iva_retenido_ingresos,
            "iva_neto_a_pagar": iva_neto,
            "num_facturas_ingreso": len(ingresos),
            "num_facturas_egreso": len(egresos),
        },
        "detalle_ingresos": detalle_ingresos,
        "detalle_egresos": detalle_egresos,
    }


@app.get("/resico/reporte-isr-retenido/{ano}/{mes}", tags=["RESICO"])
async def resico_reporte_isr_retenido(
    ano: int,
    mes: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reporte ISR Retenido mensual (RESICO PF — Art. 113-J LISR):
    Cuando una Persona Moral paga a un RESICO PF, le retiene 1.25% de ISR.
    Este reporte muestra todas las retenciones recibidas en el período.
    El ISR retenido se acredita contra el ISR mensual del RESICO.
    """
    primer_dia = datetime(ano, mes, 1)
    ultimo_dia = datetime(ano, mes, calendar.monthrange(ano, mes)[1], 23, 59, 59)

    facturas = db.query(Factura).filter(
        Factura.tenant_id == current_user.tenant_id,
        Factura.fecha_emision >= primer_dia,
        Factura.fecha_emision <= ultimo_dia,
        Factura.tipo == "ingreso",
        Factura.estado != "cancelada",
    ).all()

    con_retencion = [f for f in facturas if (getattr(f, "isr_retenido", 0) or 0) > 0]
    total_isr_retenido = round(sum(getattr(f, "isr_retenido", 0) or 0 for f in con_retencion), 2)
    total_ingresos_con_ret = round(sum(f.subtotal or 0 for f in con_retencion), 2)

    # Verificación: 1.25% de los ingresos con retención
    tasa_efectiva = round((total_isr_retenido / total_ingresos_con_ret * 100), 4) if total_ingresos_con_ret > 0 else 0

    detalle = [{
        "uuid": f.uuid_cfdi, "folio": f.folio,
        "rfc_receptor": f.rfc_receptor,
        "nombre_receptor": getattr(f, "nombre_receptor", ""),
        "subtotal": f.subtotal,
        "isr_retenido": getattr(f, "isr_retenido", 0) or 0,
        "tasa_pct": round(((getattr(f, "isr_retenido", 0) or 0) / f.subtotal * 100), 4) if f.subtotal else 0,
        "iva": f.iva,
        "total": f.total,
        "fecha": str(f.fecha_emision)[:10],
        "regimen": getattr(f, "regimen_fiscal", "general"),
        "tipo_pago": getattr(f, "tipo_pago", "pendiente") or "pendiente",
    } for f in con_retencion]

    return {
        "periodo": f"{ano}-{mes:02d}",
        "tenant_id": current_user.tenant_id,
        "regimen_aplicable": "RESICO PF — Art. 113-J LISR",
        "resumen": {
            "total_isr_retenido": total_isr_retenido,
            "total_ingresos_con_retencion": total_ingresos_con_ret,
            "tasa_efectiva_pct": tasa_efectiva,
            "num_cfdi_con_retencion": len(con_retencion),
            "num_cfdi_sin_retencion": len(facturas) - len(con_retencion),
        },
        "detalle": detalle,
    }


@app.get("/resico/resumen/{ano}/{mes}", tags=["RESICO"])
async def resico_resumen_fiscal(
    ano: int,
    mes: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dashboard fiscal RESICO: ingresos, ISR, IVA y estados de pago en un solo endpoint."""
    iva_rep = await resico_reporte_iva(ano, mes, current_user, db)
    isr_rep = await resico_reporte_isr_retenido(ano, mes, current_user, db)

    # Estados de pago del mes
    primer_dia = datetime(ano, mes, 1)
    ultimo_dia = datetime(ano, mes, calendar.monthrange(ano, mes)[1], 23, 59, 59)
    facturas = db.query(Factura).filter(
        Factura.tenant_id == current_user.tenant_id,
        Factura.fecha_emision >= primer_dia,
        Factura.fecha_emision <= ultimo_dia,
    ).all()

    def _sum(lst, key="total"): return round(sum(getattr(f, key, 0) or 0 for f in lst), 2)

    ing = [f for f in facturas if f.tipo == "ingreso" and f.estado != "cancelada"]
    egr = [f for f in facturas if f.tipo == "gasto" and f.estado != "cancelada"]

    pagadas = [f for f in ing if (getattr(f, "tipo_pago", "") or "") == "pagado"]
    pendientes = [f for f in ing if (getattr(f, "tipo_pago", "") or "") in ("pendiente", "")]
    prepagadas = [f for f in ing if (getattr(f, "tipo_pago", "") or "") == "prepagado"]

    return {
        "periodo": f"{ano}-{mes:02d}",
        "tenant_id": current_user.tenant_id,
        "ingresos": {
            "total": _sum(ing),
            "pagado": _sum(pagadas),
            "pendiente": _sum(pendientes),
            "prepagado": _sum(prepagadas),
            "num_cfdi": len(ing),
        },
        "egresos": {
            "total": _sum(egr),
            "num_cfdi": len(egr),
        },
        "iva": iva_rep["resumen"],
        "isr_retenido": isr_rep["resumen"],
    }


# ═══════════════════════════════════════════════
#  ADMIN — MULTI-TENANT
# ═══════════════════════════════════════════════

@app.get("/admin/tenants", tags=["Admin"])
async def admin_list_tenants(
    current_user: Usuario = Depends(require_role("admin", "ceo")),
    db: Session = Depends(get_db),
):
    """Lista todos los tenants con métricas básicas (solo admin/ceo)."""
    tenants = db.query(Tenant).filter(Tenant.activo == True).all()
    result = []
    for t in tenants:
        usuarios = db.query(Usuario).filter(Usuario.tenant_id == t.id, Usuario.activo == True).count()
        facturas = db.query(Factura).filter(Factura.tenant_id == t.id).count()
        ingresos = db.query(Factura).filter(
            Factura.tenant_id == t.id, Factura.tipo == "ingreso"
        ).with_entities(func.sum(Factura.total)).scalar() or 0
        result.append({
            "id": t.id,
            "nombre": t.nombre,
            "rfc": t.rfc,
            "plan": t.plan,
            "activo": t.activo,
            "usuarios": usuarios,
            "facturas": facturas,
            "ingresos_total": round(ingresos, 2),
            "created_at": str(t.created_at),
        })
    return result


@app.patch("/admin/tenants/{tenant_id}/plan", tags=["Admin"])
async def admin_update_plan(
    tenant_id: str,
    body: dict,
    current_user: Usuario = Depends(require_role("admin", "ceo")),
    db: Session = Depends(get_db),
):
    """Actualiza el plan de un tenant."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")
    plan = body.get("plan", tenant.plan)
    if plan not in ("basico", "business", "pro", "magia"):
        raise HTTPException(status_code=400, detail="Plan inválido. Usa: basico, business, pro, magia")
    tenant.plan = plan
    db.commit()
    return {"ok": True, "tenant_id": tenant_id, "plan": plan}


@app.get("/admin/tenants/{tenant_id}/cierre/{ano}/{mes}", tags=["Admin"])
async def admin_tenant_cierre(
    tenant_id: str,
    ano: int,
    mes: int,
    current_user: Usuario = Depends(require_role("admin", "ceo")),
    db: Session = Depends(get_db),
):
    """Cierre de cualquier tenant (solo admin/ceo)."""
    # Simular usuario del tenant
    fake_user = type("U", (), {"tenant_id": tenant_id, "rol": "admin"})()
    return await cierre_mes(ano, mes, fake_user, db)


# ═══════════════════════════════════════════════
#  MERCADO PAGO — SUSCRIPCIONES
# ═══════════════════════════════════════════════

_MP_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN", "")
_PLANES_PRECIOS = {
    "basico":   {"mxn": 499,  "label": "Básico"},
    "business": {"mxn": 999,  "label": "Business"},
    "pro":      {"mxn": 1999, "label": "Pro"},
    "magia":    {"mxn": 3999, "label": "Magia IA"},
}


@app.post("/payments/mp/preference", tags=["Pagos"])
async def mp_create_preference(
    body: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea una preferencia de pago en Mercado Pago para suscripción mensual."""
    plan = body.get("plan", "basico")
    if plan not in _PLANES_PRECIOS:
        raise HTTPException(status_code=400, detail=f"Plan inválido: {plan}")

    precio = _PLANES_PRECIOS[plan]
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")

    if not _MP_ACCESS_TOKEN:
        return {
            "error": "MP_ACCESS_TOKEN no configurado",
            "hint": "Agrega MP_ACCESS_TOKEN al docker-compose.vps.yml"
        }

    import httpx
    payload = {
        "items": [{
            "title": f"Mystic AI — Plan {precio['label']}",
            "quantity": 1,
            "unit_price": precio["mxn"],
            "currency_id": "MXN",
        }],
        "payer": {
            "email": current_user.email,
            "name": current_user.nombre,
        },
        "external_reference": f"{current_user.tenant_id}:{plan}",
        "notification_url": f"{os.environ.get('API_BASE_URL', 'https://sonoradigitalcorp.com/api')}/payments/mp/webhook",
        "back_urls": {
            "success": f"{os.environ.get('FRONTEND_URL', 'https://sonoradigitalcorp.com')}/panel/billing?status=success",
            "failure": f"{os.environ.get('FRONTEND_URL', 'https://sonoradigitalcorp.com')}/panel/billing?status=failure",
            "pending": f"{os.environ.get('FRONTEND_URL', 'https://sonoradigitalcorp.com')}/panel/billing?status=pending",
        },
        "auto_return": "approved",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as http:
            r = await http.post(
                "https://api.mercadopago.com/checkout/preferences",
                json=payload,
                headers={
                    "Authorization": f"Bearer {_MP_ACCESS_TOKEN}",
                    "Content-Type": "application/json",
                },
            )
            data = r.json()
            if r.status_code == 201:
                return {
                    "preference_id": data["id"],
                    "init_point": data["init_point"],
                    "sandbox_init_point": data.get("sandbox_init_point"),
                    "plan": plan,
                    "monto": precio["mxn"],
                }
            return {"error": data.get("message", "Error MP"), "detail": data}
    except Exception as e:
        return {"error": str(e)}


@app.post("/payments/mp/webhook", tags=["Pagos"])
async def mp_webhook(
    body: dict,
    db: Session = Depends(get_db),
):
    """Recibe notificaciones de pago de Mercado Pago y actualiza el plan del tenant."""
    mp_type = body.get("type") or body.get("action", "")
    mp_data = body.get("data", {})
    payment_id = mp_data.get("id") or body.get("id")

    if mp_type not in ("payment", "payment.created", "payment.updated"):
        return {"ok": True, "skipped": True}

    if not _MP_ACCESS_TOKEN or not payment_id:
        return {"ok": False, "reason": "no token or id"}

    import httpx
    try:
        async with httpx.AsyncClient(timeout=10) as http:
            r = await http.get(
                f"https://api.mercadopago.com/v1/payments/{payment_id}",
                headers={"Authorization": f"Bearer {_MP_ACCESS_TOKEN}"},
            )
            pago = r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

    status = pago.get("status")
    external_ref = pago.get("external_reference", "")

    if status == "approved" and ":" in external_ref:
        tenant_id, plan = external_ref.split(":", 1)
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if tenant and plan in _PLANES_PRECIOS:
            tenant.plan = plan
            db.commit()
            logger.info(f"[MP] Tenant {tenant_id} actualizado a plan {plan} — pago {payment_id}")

    return {"ok": True, "status": status}


@app.get("/payments/planes", tags=["Pagos"])
async def get_planes():
    """Retorna los planes disponibles y sus precios."""
    return [
        {"id": k, "label": v["label"], "precio_mxn": v["mxn"]}
        for k, v in _PLANES_PRECIOS.items()
    ]


# ═══════════════════════════════════════════════
#  CONTADOR — DASHBOARD MULTI-CLIENTE
# ═══════════════════════════════════════════════

@app.get("/contador/clientes", tags=["Contador"])
async def contador_list_clientes(
    current_user: Usuario = Depends(require_role("contador", "admin", "ceo")),
    db: Session = Depends(get_db),
):
    """Lista todos los clientes del contador con métricas fiscales del mes actual."""
    now = datetime.now(timezone.utc)
    mes_inicio = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

    tenants = db.query(Tenant).filter(Tenant.activo == True).all()
    result = []
    for t in tenants:
        facturas_mes = db.query(Factura).filter(
            Factura.tenant_id == t.id,
            Factura.fecha_emision >= mes_inicio,
        ).count()

        ingresos_mes = db.query(func.sum(Factura.total)).filter(
            Factura.tenant_id == t.id, Factura.tipo == "ingreso",
            Factura.fecha_emision >= mes_inicio,
        ).scalar() or 0

        egresos_mes = db.query(func.sum(Factura.total)).filter(
            Factura.tenant_id == t.id, Factura.tipo == "egreso",
            Factura.fecha_emision >= mes_inicio,
        ).scalar() or 0

        iva_cobrado = db.query(func.sum(Factura.iva)).filter(
            Factura.tenant_id == t.id, Factura.tipo == "ingreso",
            Factura.fecha_emision >= mes_inicio,
        ).scalar() or 0

        iva_acreditable = db.query(func.sum(Factura.iva)).filter(
            Factura.tenant_id == t.id, Factura.tipo == "egreso",
            Factura.fecha_emision >= mes_inicio,
        ).scalar() or 0

        isr_ret = db.query(func.sum(Factura.isr_retenido)).filter(
            Factura.tenant_id == t.id, Factura.tipo == "ingreso",
            Factura.fecha_emision >= mes_inicio,
        ).scalar() or 0

        # Facturas sin pago asignado (pendientes de tipo_pago)
        pendientes_pago = db.query(Factura).filter(
            Factura.tenant_id == t.id,
            Factura.tipo_pago == "pendiente",
            Factura.tipo == "ingreso",
        ).count()

        cierre = db.query(CierreMes).filter(
            CierreMes.tenant_id == t.id,
            getattr(CierreMes, "año") == now.year,
            CierreMes.mes == now.month,
        ).first()

        # Semáforo fiscal
        if facturas_mes > 0 and cierre and cierre.estado == "cerrado":
            semaforo = "green"
        elif facturas_mes > 0:
            semaforo = "yellow"
        else:
            semaforo = "red"

        result.append({
            "id": t.id,
            "nombre": t.nombre,
            "rfc": t.rfc,
            "plan": t.plan,
            "facturas_mes": facturas_mes,
            "ingresos_mes": round(ingresos_mes, 2),
            "egresos_mes": round(egresos_mes, 2),
            "iva_neto_mes": round(iva_cobrado - iva_acreditable, 2),
            "isr_retenido_mes": round(isr_ret, 2),
            "pendientes_pago": pendientes_pago,
            "tiene_cierre": cierre is not None,
            "estado_cierre": cierre.estado if cierre else None,
            "semaforo": semaforo,
        })
    return result


@app.post("/contador/xmls/bulk", tags=["Contador"])
async def contador_bulk_xml(
    files: List[UploadFile] = File(...),
    current_user: Usuario = Depends(require_role("contador", "admin", "ceo")),
    db: Session = Depends(get_db),
):
    """Carga múltiples XMLs CFDI y los asigna automáticamente por RFC del emisor/receptor."""
    results = []
    for file in files:
        try:
            content = await file.read()
            xml_str = content.decode("utf-8", errors="ignore")
            parsed = _parsear_cfdi(xml_str)

            rfc_emisor = parsed.get("rfc_emisor", "")
            rfc_receptor = parsed.get("rfc_receptor", "")

            # Auto-asignar tenant por RFC
            tenant = db.query(Tenant).filter(
                Tenant.activo == True
            ).filter(
                (Tenant.rfc == rfc_emisor) | (Tenant.rfc == rfc_receptor)
            ).first()

            if not tenant:
                results.append({
                    "file": file.filename, "ok": False,
                    "error": f"Sin tenant para RFC {rfc_emisor}/{rfc_receptor}",
                })
                continue

            tipo = "ingreso" if tenant.rfc == rfc_emisor else "egreso"

            # Verificar duplicado
            if parsed.get("uuid_cfdi") and db.query(Factura).filter(
                Factura.tenant_id == tenant.id,
                Factura.uuid_cfdi == parsed.get("uuid_cfdi"),
            ).first():
                results.append({
                    "file": file.filename, "ok": False,
                    "error": "UUID duplicado", "tenant": tenant.nombre,
                })
                continue

            factura = Factura(
                tenant_id=tenant.id, tipo=tipo,
                uuid_cfdi=parsed.get("uuid_cfdi"),
                rfc_emisor=rfc_emisor, rfc_receptor=rfc_receptor,
                nombre_emisor=parsed.get("nombre_emisor"),
                nombre_receptor=parsed.get("nombre_receptor"),
                subtotal=parsed.get("subtotal", 0),
                iva=parsed.get("iva", 0),
                total=parsed.get("total", 0),
                moneda=parsed.get("moneda", "MXN"),
                tipo_cambio=parsed.get("tipo_cambio", 1.0),
                fecha_emision=parsed.get("fecha_emision"),
                concepto=parsed.get("concepto"),
                isr_retenido=parsed.get("isr_retenido", 0),
                iva_retenido=parsed.get("iva_retenido", 0),
                regimen_fiscal=parsed.get("regimen_fiscal", "general"),
                tipo_pago="pendiente",
                xml_cfdi=xml_str,
            )
            db.add(factura)
            db.commit()

            results.append({
                "file": file.filename, "ok": True,
                "tenant": tenant.nombre, "rfc": tenant.rfc,
                "tipo": tipo,
                "total": parsed.get("total", 0),
                "uuid": parsed.get("uuid_cfdi"),
            })
        except Exception as e:
            results.append({"file": file.filename, "ok": False, "error": str(e)})

    ok_count = sum(1 for r in results if r.get("ok"))
    return {"total": len(results), "ok": ok_count, "errores": len(results) - ok_count, "detalle": results}


@app.get("/contador/clientes/{tenant_id}/facturas", tags=["Contador"])
async def contador_cliente_facturas(
    tenant_id: str,
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    current_user: Usuario = Depends(require_role("contador", "admin", "ceo")),
    db: Session = Depends(get_db),
):
    """Facturas de un cliente específico con filtro de mes/año."""
    now = datetime.now(timezone.utc)
    ano = ano or now.year
    mes = mes or now.month
    mes_inicio = datetime(ano, mes, 1, tzinfo=timezone.utc)
    import calendar as _cal
    mes_fin = datetime(ano, mes, _cal.monthrange(ano, mes)[1], 23, 59, 59, tzinfo=timezone.utc)

    facturas = db.query(Factura).filter(
        Factura.tenant_id == tenant_id,
        Factura.fecha_emision >= mes_inicio,
        Factura.fecha_emision <= mes_fin,
    ).order_by(Factura.fecha_emision.desc()).all()

    return [
        {
            "id": f.id,
            "tipo": f.tipo,
            "folio": f.folio,
            "uuid_cfdi": f.uuid_cfdi,
            "rfc_emisor": f.rfc_emisor,
            "nombre_emisor": f.nombre_emisor,
            "rfc_receptor": f.rfc_receptor,
            "nombre_receptor": f.nombre_receptor,
            "subtotal": f.subtotal,
            "iva": f.iva,
            "total": f.total,
            "isr_retenido": f.isr_retenido,
            "iva_retenido": f.iva_retenido,
            "tipo_pago": f.tipo_pago,
            "regimen_fiscal": f.regimen_fiscal,
            "estado": f.estado,
            "fecha_emision": str(f.fecha_emision),
            "concepto": f.concepto,
        }
        for f in facturas
    ]
