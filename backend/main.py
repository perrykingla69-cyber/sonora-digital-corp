"""
MYSTIC — API Unificada
Fusiona el AI OS (orquestador de agentes) con todos los endpoints contables.
Puerto: 8000 (producción en Docker) | 8002 (standalone local)
"""

from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
BACKEND = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BACKEND))

# ── Imports internos ──────────────────────────────────────────────────────────
from database import Base, engine, get_db
from models import (
    AlertaConfig, AuditLog, CierreMes, Empleado, Factura,
    GSDTask, Lead, MVE, Nomina, Tenant, TipoCambio, Usuario,
)
from security import (
    create_token, get_current_user, hash_password,
    require_role, verify_password,
)
from calculos_completos_147 import CalculosCompletos147
from orchestrator.orchestrator import Orchestrator
from memory.task_history import TaskHistory
from memory.knowledge_store import KnowledgeStore
from memory.vector_memory import VectorMemory

# ── Config ────────────────────────────────────────────────────────────────────
CONFIGS_DIR = ROOT / "configs"
DATA_DIR = BACKEND / ".data"
DATA_DIR.mkdir(exist_ok=True)

calc = CalculosCompletos147()
orchestrator: Orchestrator = None

DOF_API = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/oportuno"
BANXICO_TOKEN = os.getenv("BANXICO_TOKEN", "")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    # Inicializar orquestador AI OS
    try:
        orchestrator = Orchestrator.from_config(
            agents_config=str(CONFIGS_DIR / "agents.yaml"),
            skills_config=str(CONFIGS_DIR / "skills.yaml"),
        )
        orchestrator.task_history = TaskHistory(persist_path=str(DATA_DIR / "tasks.json"))
        orchestrator.knowledge_store = KnowledgeStore(persist_path=str(DATA_DIR / "knowledge.json"))
    except Exception as e:
        import warnings
        warnings.warn(f"AI OS no inicializado: {e}")
    yield


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="MYSTIC Platform API",
    description="AI Operating System + Contabilidad para Sonora Digital Corp",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    email: str
    password: str

class TenantCreate(BaseModel):
    nombre: str
    rfc: str
    direccion: str = ""
    plan: str = "basico"

class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    password: str
    rol: str = "contador"
    tenant_id: str

class FacturaCreate(BaseModel):
    tipo: str = "ingreso"
    folio: str = ""
    rfc_emisor: str = ""
    rfc_receptor: str = ""
    nombre_emisor: str = ""
    nombre_receptor: str = ""
    subtotal: float = 0.0
    iva: float = 0.0
    total: float = 0.0
    moneda: str = "MXN"
    tipo_cambio: float = 1.0
    concepto: str = ""
    fecha_emision: Optional[datetime] = None

class GSDTaskCreate(BaseModel):
    titulo: str
    descripcion: str = ""
    prioridad: int = 1
    fecha_limite: Optional[datetime] = None

class MVECreate(BaseModel):
    numero_pedimento: str = ""
    aduana: str = ""
    valor_comercial: float = 0.0
    moneda: str = "USD"
    tipo_cambio: float = 1.0
    fraccion_arancelaria: str = ""
    descripcion: str = ""
    igi_porcentaje: float = 0.0
    incoterm: str = "CIF"

class LeadCreate(BaseModel):
    nombre: str
    empresa: str = ""
    email: str = ""
    telefono: str = ""
    status: str = "nuevo"
    notas: str = ""

class LeadUpdate(BaseModel):
    nombre: Optional[str] = None
    empresa: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    status: Optional[str] = None
    notas: Optional[str] = None

# AI OS schemas
class TaskPayload(BaseModel):
    skill: str
    args: dict[str, Any] = Field(default_factory=dict)

class TaskRequest(BaseModel):
    id: Optional[str] = None
    agent: Optional[str] = None
    capability: Optional[str] = None
    payload: TaskPayload

class SwarmRequest(BaseModel):
    tasks: list[TaskRequest]

class KnowledgePutRequest(BaseModel):
    key: str
    value: Any

class VectorAddRequest(BaseModel):
    key: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class SearchRequest(BaseModel):
    query: str
    limit: int = 5


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _tenant_id(user) -> str:
    if hasattr(user, "tenant_id"):
        return user.tenant_id
    return user.get("tenant_id") or ""

def _log(db, accion, recurso, user=None, detalle=None):
    try:
        entry = AuditLog(
            tenant_id=_tenant_id(user) if user else None,
            usuario_id=getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else None),
            accion=accion,
            recurso=recurso,
            detalle=detalle or {},
        )
        db.add(entry)
        db.commit()
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# SISTEMA
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/", tags=["sistema"])
def root():
    return {"system": "MYSTIC Platform", "version": "2.0.0", "status": "running"}

@app.get("/health", tags=["sistema"])
def health():
    return {"status": "ok"}

@app.get("/status", tags=["sistema"])
def status(db: Session = Depends(get_db)):
    ai_status = orchestrator.status() if orchestrator else {"agents": [], "skills": []}
    tenants = db.query(Tenant).count()
    usuarios = db.query(Usuario).count()
    facturas = db.query(Factura).count()
    return {
        "status": "ok",
        "tenants": tenants,
        "usuarios": usuarios,
        "facturas": facturas,
        "ai_os": ai_status,
    }


# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/auth/login", tags=["auth"])
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = create_token(user.id, {"rol": user.rol, "tenant_id": user.tenant_id, "nombre": user.nombre})
    return {"access_token": token, "token_type": "bearer", "rol": user.rol, "nombre": user.nombre}

@app.post("/auth/registro", tags=["auth"])
def registro(req: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    user = Usuario(
        nombre=req.nombre,
        email=req.email,
        password_hash=hash_password(req.password),
        rol=req.rol,
        tenant_id=req.tenant_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "rol": user.rol}


# ══════════════════════════════════════════════════════════════════════════════
# TENANTS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/tenants", tags=["tenants"])
def list_tenants(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Tenant).all()

@app.post("/tenants", tags=["tenants"])
def create_tenant(req: TenantCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    tenant = Tenant(**req.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


# ══════════════════════════════════════════════════════════════════════════════
# FACTURAS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/facturas", tags=["facturas"])
def list_facturas(
    tipo: Optional[str] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(Factura).filter(Factura.tenant_id == _tenant_id(user))
    if tipo:
        q = q.filter(Factura.tipo == tipo)
    if estado:
        q = q.filter(Factura.estado == estado)
    return q.order_by(Factura.created_at.desc()).all()

@app.post("/facturas", tags=["facturas"])
def create_factura(req: FacturaCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    f = Factura(**req.model_dump(), tenant_id=_tenant_id(user))
    if not f.iva:
        f.iva = round(f.subtotal * 0.16, 2)
    if not f.total:
        f.total = round(f.subtotal + f.iva, 2)
    db.add(f)
    db.commit()
    db.refresh(f)
    _log(db, "create", "factura", user, {"id": f.id})
    return f

@app.get("/facturas/{factura_id}", tags=["facturas"])
def get_factura(factura_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    f = db.query(Factura).filter(Factura.id == factura_id, Factura.tenant_id == _tenant_id(user)).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return f

@app.patch("/facturas/{factura_id}/pagar", tags=["facturas"])
def pagar_factura(factura_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    f = db.query(Factura).filter(Factura.id == factura_id, Factura.tenant_id == _tenant_id(user)).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    f.estado = "pagada"
    f.fecha_pago = datetime.now(timezone.utc)
    db.commit()
    return {"status": "pagada", "id": factura_id}

@app.patch("/facturas/{factura_id}/cancelar", tags=["facturas"])
def cancelar_factura(factura_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    f = db.query(Factura).filter(Factura.id == factura_id, Factura.tenant_id == _tenant_id(user)).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    f.estado = "cancelada"
    db.commit()
    return {"status": "cancelada", "id": factura_id}

@app.post("/facturas/xml", tags=["facturas"])
async def upload_cfdi_xml(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Parsea CFDI 4.0/3.3 XML y crea factura automáticamente."""
    content = await file.read()
    try:
        root = ET.fromstring(content.decode("utf-8"))
        ns = {"cfdi": "http://www.sat.gob.mx/cfd/4", "cfdi3": "http://www.sat.gob.mx/cfd/3"}

        # Detectar versión
        version = root.get("Version") or root.get("version", "4.0")
        ns_key = "cfdi" if version.startswith("4") else "cfdi3"

        comprobante = root
        emisor = root.find(f"{ns_key}:Emisor", ns) or root.find("cfdi3:Emisor", ns)
        receptor = root.find(f"{ns_key}:Receptor", ns) or root.find("cfdi3:Receptor", ns)
        impuestos = root.find(f"{ns_key}:Impuestos", ns) or root.find("cfdi3:Impuestos", ns)

        subtotal = float(comprobante.get("SubTotal", 0))
        total = float(comprobante.get("Total", 0))
        tipo_doc = comprobante.get("TipoDeComprobante", "I")
        tipo = "ingreso" if tipo_doc == "I" else "egreso"

        iva = 0.0
        if impuestos is not None:
            iva = float(impuestos.get("TotalImpuestosTrasladados", 0))

        f = Factura(
            tenant_id=_tenant_id(user),
            tipo=tipo,
            folio=comprobante.get("Folio", ""),
            uuid_cfdi=root.find(".//{http://www.sat.gob.mx/TimbreFiscalDigital}TimbreFiscalDigital", {})
                        .get("UUID", "") if root.find(".//{http://www.sat.gob.mx/TimbreFiscalDigital}TimbreFiscalDigital", {}) is not None else "",
            rfc_emisor=emisor.get("Rfc", "") if emisor is not None else "",
            nombre_emisor=emisor.get("Nombre", "") if emisor is not None else "",
            rfc_receptor=receptor.get("Rfc", "") if receptor is not None else "",
            nombre_receptor=receptor.get("Nombre", "") if receptor is not None else "",
            subtotal=subtotal,
            iva=iva,
            total=total,
            moneda=comprobante.get("Moneda", "MXN"),
            tipo_cambio=float(comprobante.get("TipoCambio", 1.0)),
            concepto=f"CFDI {version} importado",
            xml_cfdi=content.decode("utf-8"),
        )
        db.add(f)
        db.commit()
        db.refresh(f)
        return {"status": "ok", "id": f.id, "total": total, "tipo": tipo}
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"XML inválido: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD / CIERRE
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/dashboard", tags=["reportes"])
def dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    tid = _tenant_id(user)
    now = datetime.now(timezone.utc)
    mes, año = now.month, now.year

    ingresos = db.query(Factura).filter(
        Factura.tenant_id == tid, Factura.tipo == "ingreso",
        Factura.estado != "cancelada",
    ).all()
    egresos = db.query(Factura).filter(
        Factura.tenant_id == tid, Factura.tipo == "egreso",
        Factura.estado != "cancelada",
    ).all()

    total_ing = sum(f.total for f in ingresos)
    total_egr = sum(f.total for f in egresos)
    iva_cobrado = sum(f.iva for f in ingresos)
    iva_pagado = sum(f.iva for f in egresos)

    cierre = calc.generar_cierre_maestro({
        "ingresos": total_ing,
        "costo_ventas": total_egr * 0.6,
        "gastos": total_egr * 0.4,
    })

    return {
        "mes": mes, "año": año,
        "ingresos": total_ing,
        "egresos": total_egr,
        "iva_neto": round(iva_cobrado - iva_pagado, 2),
        "isr_estimado": cierre["isr_estimado"],
        "utilidad_neta": cierre["utilidad_neta"],
        "facturas_pendientes": sum(1 for f in ingresos if f.estado == "pendiente"),
        "resumen": cierre,
    }

@app.get("/cierre/{año}/{mes}", tags=["reportes"])
def cierre_mensual(año: int, mes: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    tid = _tenant_id(user)
    ingresos = db.query(Factura).filter(Factura.tenant_id == tid, Factura.tipo == "ingreso").all()
    egresos = db.query(Factura).filter(Factura.tenant_id == tid, Factura.tipo == "egreso").all()
    total_ing = sum(f.total for f in ingresos)
    total_egr = sum(f.total for f in egresos)
    cierre = calc.generar_cierre_maestro({"ingresos": total_ing, "costo_ventas": total_egr * 0.6, "gastos": total_egr * 0.4})
    return {"año": año, "mes": mes, "cierre": cierre, "facturas_ingreso": len(ingresos), "facturas_egreso": len(egresos)}

@app.get("/tipo-cambio/hoy", tags=["reportes"])
async def tipo_cambio_hoy(db: Session = Depends(get_db)):
    # 1. Buscar en BD del día
    hoy = datetime.now(timezone.utc).date()
    tc = db.query(TipoCambio).filter(TipoCambio.fecha >= datetime(hoy.year, hoy.month, hoy.day, tzinfo=timezone.utc)).first()
    if tc:
        return {"usd_mxn": tc.usd_mxn, "fecha": tc.fecha, "fuente": tc.fuente}
    # 2. Consultar Banxico (fallback: valor fijo)
    try:
        headers = {"Bmx-Token": BANXICO_TOKEN} if BANXICO_TOKEN else {}
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(DOF_API, headers=headers)
            data = r.json()
            valor = float(data["bmx"]["series"][0]["datos"][0]["dato"])
    except Exception:
        valor = 17.15  # fallback
    tc_new = TipoCambio(usd_mxn=valor, fuente="Banxico/fallback")
    db.add(tc_new)
    db.commit()
    return {"usd_mxn": valor, "fecha": datetime.now(timezone.utc).isoformat(), "fuente": "Banxico"}


# ══════════════════════════════════════════════════════════════════════════════
# GSD TASKS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/gsd/tasks", tags=["gsd"])
def list_gsd_tasks(db: Session = Depends(get_db), user=Depends(get_current_user)):
    uid = getattr(user, "id", None) or user.get("id")
    return db.query(GSDTask).filter(GSDTask.usuario_id == uid, GSDTask.completada == False).order_by(GSDTask.prioridad).all()

@app.post("/gsd/tasks", tags=["gsd"])
def create_gsd_task(req: GSDTaskCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    uid = getattr(user, "id", None) or user.get("id")
    tid = _tenant_id(user)
    count = db.query(GSDTask).filter(GSDTask.usuario_id == uid, GSDTask.prioridad == 1, GSDTask.completada == False).count()
    if req.prioridad == 1 and count >= 3:
        raise HTTPException(status_code=400, detail="Máximo 3 MITs activos (prioridad 1)")
    task = GSDTask(**req.model_dump(), usuario_id=uid, tenant_id=tid)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.patch("/gsd/tasks/{task_id}/done", tags=["gsd"])
def complete_gsd_task(task_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    uid = getattr(user, "id", None) or user.get("id")
    task = db.query(GSDTask).filter(GSDTask.id == task_id, GSDTask.usuario_id == uid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    task.completada = True
    db.commit()
    return {"status": "completada", "id": task_id}

@app.delete("/gsd/tasks/{task_id}", tags=["gsd"])
def delete_gsd_task(task_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    uid = getattr(user, "id", None) or user.get("id")
    task = db.query(GSDTask).filter(GSDTask.id == task_id, GSDTask.usuario_id == uid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    db.delete(task)
    db.commit()
    return {"status": "deleted"}


# ══════════════════════════════════════════════════════════════════════════════
# MVE — Manifestación de Valor
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/mve/calcular/preview", tags=["mve"])
def mve_preview(
    valor_comercial: float,
    tipo_cambio: float = 1.0,
    igi_porcentaje: float = 0.0,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    valor_aduana = round(valor_comercial * tipo_cambio, 2)
    result = calc.total_contribuciones_importacion(valor_aduana, igi_porcentaje)
    return result

@app.get("/mve", tags=["mve"])
def list_mves(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(MVE).filter(MVE.tenant_id == _tenant_id(user)).order_by(MVE.created_at.desc()).all()

@app.post("/mve", tags=["mve"])
def create_mve(req: MVECreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    valor_aduana = round(req.valor_comercial * req.tipo_cambio, 2)
    contribs = calc.total_contribuciones_importacion(valor_aduana, req.igi_porcentaje)
    mve = MVE(
        tenant_id=str(_tenant_id(user)),
        **req.model_dump(),
        valor_aduana_mxn=valor_aduana,
        igi_monto=contribs["igi"],
        dta=contribs["dta"],
        iva_importacion=contribs["iva_importacion"],
        total_contribuciones=contribs["total"],
    )
    db.add(mve)
    db.commit()
    db.refresh(mve)
    return mve

@app.patch("/mve/{mve_id}/folio", tags=["mve"])
def registrar_folio_vucem(
    mve_id: str,
    folio: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    mve = db.query(MVE).filter(MVE.id == mve_id, MVE.tenant_id == _tenant_id(user)).first()
    if not mve:
        raise HTTPException(status_code=404, detail="MVE no encontrada")
    mve.folio_vucem = folio
    mve.estado = "presentada"
    mve.fecha_presentacion_vucem = datetime.now(timezone.utc)
    db.commit()
    return {"status": "ok", "folio_vucem": folio}


# ══════════════════════════════════════════════════════════════════════════════
# LEADS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/leads", tags=["leads"])
def list_leads(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Lead).filter(Lead.tenant_id == _tenant_id(user)).order_by(Lead.created_at.desc()).all()

@app.post("/leads", tags=["leads"])
def create_lead(req: LeadCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    lead = Lead(**req.model_dump(), tenant_id=_tenant_id(user))
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@app.patch("/leads/{lead_id}", tags=["leads"])
def update_lead(lead_id: str, req: LeadUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.tenant_id == _tenant_id(user)).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    for k, v in req.model_dump(exclude_none=True).items():
        setattr(lead, k, v)
    db.commit()
    return lead

@app.delete("/leads/{lead_id}", tags=["leads"])
def delete_lead(lead_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.tenant_id == _tenant_id(user)).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    db.delete(lead)
    db.commit()
    return {"status": "deleted"}


# ══════════════════════════════════════════════════════════════════════════════
# ALERTAS CONFIG
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/alertas/config", tags=["alertas"])
def get_alerta_config(db: Session = Depends(get_db), user=Depends(get_current_user)):
    config = db.query(AlertaConfig).filter(AlertaConfig.tenant_id == _tenant_id(user)).first()
    if not config:
        config = AlertaConfig(tenant_id=_tenant_id(user))
        db.add(config)
        db.commit()
    return config

@app.patch("/alertas/config", tags=["alertas"])
def update_alerta_config(
    hora_manana: Optional[str] = None,
    hora_tarde: Optional[str] = None,
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    config = db.query(AlertaConfig).filter(AlertaConfig.tenant_id == _tenant_id(user)).first()
    if not config:
        config = AlertaConfig(tenant_id=_tenant_id(user))
        db.add(config)
    if hora_manana:
        config.hora_manana = hora_manana
    if hora_tarde:
        config.hora_tarde = hora_tarde
    if activo is not None:
        config.activo = activo
    db.commit()
    return config


# ══════════════════════════════════════════════════════════════════════════════
# LOGS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/logs", tags=["sistema"])
def get_logs(limit: int = 50, db: Session = Depends(get_db), user=Depends(require_role("ceo", "admin"))):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()


# ══════════════════════════════════════════════════════════════════════════════
# CÁLCULOS FISCALES
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/calculos/isr", tags=["calculos"])
def calcular_isr_endpoint(utilidad: float, user=Depends(get_current_user)):
    return {
        "utilidad": utilidad,
        "isr": calc.isr_base(utilidad),
        "ptu": calc.ptu(utilidad),
    }

@app.get("/calculos/nomina", tags=["calculos"])
def calcular_nomina_endpoint(salario_bruto: float, user=Depends(get_current_user)):
    return calc.salario_neto(salario_bruto)

@app.get("/calculos/importacion", tags=["calculos"])
def calcular_importacion_endpoint(
    valor_aduana: float,
    igi_porcentaje: float = 0.0,
    user=Depends(get_current_user),
):
    return calc.total_contribuciones_importacion(valor_aduana, igi_porcentaje)


# ══════════════════════════════════════════════════════════════════════════════
# AI OS — ORQUESTADOR
# ══════════════════════════════════════════════════════════════════════════════

def _require_orchestrator():
    if not orchestrator:
        raise HTTPException(status_code=503, detail="AI OS no disponible")

@app.get("/ai/status", tags=["ai-os"])
def ai_status():
    _require_orchestrator()
    return orchestrator.status()

@app.get("/ai/agents", tags=["ai-os"])
def ai_agents():
    _require_orchestrator()
    return [{"name": a.name, "role": a.instance.role, "capabilities": a.capabilities, "skills": a.instance.list_skills()} for a in orchestrator.agent_registry.list_agents()]

@app.get("/ai/skills", tags=["ai-os"])
def ai_skills():
    _require_orchestrator()
    return [{"name": s.name, "description": s.description} for s in orchestrator.skill_registry.list_skills()]

@app.post("/ai/task", tags=["ai-os"])
def ai_execute_task(req: TaskRequest, user=Depends(get_current_user)):
    _require_orchestrator()
    task = req.model_dump(exclude_none=True)
    task["payload"] = req.payload.model_dump()
    try:
        return orchestrator.execute_task(task)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ai/swarm", tags=["ai-os"])
def ai_execute_swarm(req: SwarmRequest, user=Depends(get_current_user)):
    _require_orchestrator()
    tasks = [{**t.model_dump(exclude_none=True), "payload": t.payload.model_dump()} for t in req.tasks]
    results = orchestrator.execute_swarm(tasks)
    return {"total": len(results), "results": results}

@app.get("/ai/memory/tasks", tags=["ai-os"])
def ai_memory_tasks(limit: int = 10, user=Depends(get_current_user)):
    _require_orchestrator()
    return [{"task_id": r.task_id, "task": r.task, "result": r.result, "timestamp": r.timestamp} for r in orchestrator.task_history.recent(limit)]

@app.get("/ai/memory/knowledge", tags=["ai-os"])
def ai_list_knowledge(user=Depends(get_current_user)):
    _require_orchestrator()
    return {"keys": orchestrator.knowledge_store.keys()}

@app.post("/ai/memory/knowledge", tags=["ai-os"])
def ai_put_knowledge(req: KnowledgePutRequest, user=Depends(get_current_user)):
    _require_orchestrator()
    orchestrator.knowledge_store.put(req.key, req.value)
    return {"status": "ok", "key": req.key}

@app.get("/ai/memory/knowledge/{key}", tags=["ai-os"])
def ai_get_knowledge(key: str, user=Depends(get_current_user)):
    _require_orchestrator()
    value = orchestrator.knowledge_store.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Clave '{key}' no encontrada")
    return {"key": key, "value": value}

@app.post("/ai/memory/knowledge/search", tags=["ai-os"])
def ai_search_knowledge(req: SearchRequest, user=Depends(get_current_user)):
    _require_orchestrator()
    return {"query": req.query, "results": orchestrator.knowledge_store.search(req.query)}


# ══════════════════════════════════════════════════════════════════════════════
# Error handler global
# ══════════════════════════════════════════════════════════════════════════════

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": str(exc), "type": type(exc).__name__})


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
