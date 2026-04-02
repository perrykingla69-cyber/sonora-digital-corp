"""
onboarding.py — Wizard de Onboarding para HERMES

Endpoints:
POST /api/onboarding/start          — inicia sesión, retorna session_id
POST /api/onboarding/step           — guarda progreso de un paso en Redis
GET  /api/onboarding/status/{sid}   — estado actual del onboarding
POST /api/onboarding/complete       — marca como completo, retorna resumen

Pasos:
  1. empresa      — RFC, nombre empresa, giro
  2. regimen      — régimen fiscal
  3. empleados    — rango de empleados
  4. integraciones — módulos a activar
  5. confirmacion — resumen para confirmar
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

# ── Redis con fallback a dict en memoria ──────────────────────────────────────

_memory_store: Dict[str, Any] = {}

try:
    import redis as _redis_lib
    _redis_client = _redis_lib.Redis(host="redis", port=6379, db=1, decode_responses=True, socket_connect_timeout=3)
    _redis_client.ping()
    REDIS_OK = True
    logger.info("Onboarding: Redis conectado en db=1")
except Exception as _e:
    _redis_client = None
    REDIS_OK = False
    logger.warning(f"Onboarding: Redis no disponible, usando memoria — {_e}")


SESSION_TTL = 60 * 60 * 2  # 2 horas


def _get(key: str) -> Optional[Dict]:
    if REDIS_OK and _redis_client:
        raw = _redis_client.get(key)
        return json.loads(raw) if raw else None
    return _memory_store.get(key)


def _set(key: str, value: Dict) -> None:
    if REDIS_OK and _redis_client:
        _redis_client.setex(key, SESSION_TTL, json.dumps(value, ensure_ascii=False))
    else:
        _memory_store[key] = value


def _session_key(sid: str) -> str:
    return f"onboarding:session:{sid}"


# ── Constantes de validación ──────────────────────────────────────────────────

GIROS_VALIDOS = {"manufactura", "comercio", "servicios", "construccion"}
REGIMENES_VALIDOS = {"personas_morales", "resico", "actividad_empresarial", "asalariados"}
EMPLEADOS_VALIDOS = {"0", "1-5", "6-20", "21+"}
MODULOS_VALIDOS = {"facturas", "nomina", "cierre_mensual", "whatsapp", "diot"}
PASOS_ORDEN = ["empresa", "regimen", "empleados", "integraciones", "confirmacion"]


# ── Modelos Pydantic ──────────────────────────────────────────────────────────

class StartResponse(BaseModel):
    session_id: str
    mensaje: str
    paso_actual: str
    total_pasos: int


class StepRequest(BaseModel):
    session_id: str = Field(..., description="UUID de sesión retornado por /start")
    step: str = Field(..., description="Nombre del paso: empresa|regimen|empleados|integraciones|confirmacion")
    data: Dict[str, Any] = Field(..., description="Datos del paso actual")


class StepResponse(BaseModel):
    session_id: str
    paso_guardado: str
    siguiente_paso: Optional[str]
    progreso: int  # 0-100
    mensaje: str


class StatusResponse(BaseModel):
    session_id: str
    paso_actual: str
    pasos_completados: List[str]
    progreso: int
    datos: Dict[str, Any]
    completado: bool
    iniciado_en: str


class CompleteRequest(BaseModel):
    session_id: str


class CompleteResponse(BaseModel):
    session_id: str
    completado: bool
    resumen: Dict[str, Any]
    mensaje: str


# ── Helpers de validación por paso ────────────────────────────────────────────

def _validar_empresa(data: Dict) -> None:
    if not data.get("rfc"):
        raise HTTPException(status_code=422, detail="El RFC es requerido")
    rfc = data["rfc"].strip().upper()
    if len(rfc) < 12 or len(rfc) > 13:
        raise HTTPException(status_code=422, detail="RFC inválido (12-13 caracteres)")
    if not data.get("nombre_empresa", "").strip():
        raise HTTPException(status_code=422, detail="El nombre de la empresa es requerido")
    giro = data.get("giro", "")
    if giro not in GIROS_VALIDOS:
        raise HTTPException(
            status_code=422,
            detail=f"Giro inválido. Opciones: {', '.join(sorted(GIROS_VALIDOS))}",
        )


def _validar_regimen(data: Dict) -> None:
    regimen = data.get("regimen_fiscal", "")
    if regimen not in REGIMENES_VALIDOS:
        raise HTTPException(
            status_code=422,
            detail=f"Régimen inválido. Opciones: {', '.join(sorted(REGIMENES_VALIDOS))}",
        )


def _validar_empleados(data: Dict) -> None:
    rango = data.get("rango_empleados", "")
    if rango not in EMPLEADOS_VALIDOS:
        raise HTTPException(
            status_code=422,
            detail=f"Rango de empleados inválido. Opciones: {', '.join(sorted(EMPLEADOS_VALIDOS))}",
        )


def _validar_integraciones(data: Dict) -> None:
    modulos = data.get("modulos", [])
    if not isinstance(modulos, list):
        raise HTTPException(status_code=422, detail="'modulos' debe ser una lista")
    invalidos = [m for m in modulos if m not in MODULOS_VALIDOS]
    if invalidos:
        raise HTTPException(
            status_code=422,
            detail=f"Módulos inválidos: {invalidos}. Válidos: {list(MODULOS_VALIDOS)}",
        )


VALIDADORES = {
    "empresa": _validar_empresa,
    "regimen": _validar_regimen,
    "empleados": _validar_empleados,
    "integraciones": _validar_integraciones,
    "confirmacion": lambda d: None,  # Sin validación adicional
}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/start", response_model=StartResponse, summary="Iniciar sesión de onboarding")
def onboarding_start():
    """
    Crea una nueva sesión de onboarding y retorna el session_id.
    La sesión tiene un TTL de 2 horas en Redis.
    """
    sid = str(uuid.uuid4())
    session = {
        "session_id": sid,
        "paso_actual": PASOS_ORDEN[0],
        "pasos_completados": [],
        "datos": {},
        "completado": False,
        "iniciado_en": datetime.utcnow().isoformat(),
    }
    _set(_session_key(sid), session)
    logger.info(f"Onboarding iniciado: session_id={sid}")
    return StartResponse(
        session_id=sid,
        mensaje="Sesión de onboarding iniciada. Completa los 5 pasos para activar Hermes.",
        paso_actual=PASOS_ORDEN[0],
        total_pasos=len(PASOS_ORDEN),
    )


@router.post("/step", response_model=StepResponse, summary="Guardar progreso de un paso")
def onboarding_step(body: StepRequest):
    """
    Guarda los datos de un paso específico del wizard.
    Valida los datos antes de guardarlos.
    """
    sid = body.session_id
    step = body.step.lower().strip()

    if step not in PASOS_ORDEN:
        raise HTTPException(
            status_code=400,
            detail=f"Paso desconocido: '{step}'. Pasos válidos: {PASOS_ORDEN}",
        )

    session = _get(_session_key(sid))
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada o expirada. Inicia una nueva sesión.",
        )

    if session.get("completado"):
        raise HTTPException(status_code=400, detail="Esta sesión de onboarding ya fue completada.")

    # Validar datos del paso
    validar = VALIDADORES.get(step)
    if validar:
        validar(body.data)

    # Guardar datos del paso
    session["datos"][step] = body.data

    # Actualizar pasos completados
    if step not in session["pasos_completados"]:
        session["pasos_completados"].append(step)

    # Calcular siguiente paso
    idx = PASOS_ORDEN.index(step)
    siguiente = PASOS_ORDEN[idx + 1] if idx + 1 < len(PASOS_ORDEN) else None
    if siguiente:
        session["paso_actual"] = siguiente

    progreso = int((len(session["pasos_completados"]) / len(PASOS_ORDEN)) * 100)
    _set(_session_key(sid), session)

    logger.info(f"Onboarding step '{step}' guardado: session_id={sid}, progreso={progreso}%")
    return StepResponse(
        session_id=sid,
        paso_guardado=step,
        siguiente_paso=siguiente,
        progreso=progreso,
        mensaje=f"Paso '{step}' guardado. {'Siguiente: ' + siguiente if siguiente else 'Todos los pasos completados.'}",
    )


@router.get("/status/{sid}", response_model=StatusResponse, summary="Estado del onboarding")
def onboarding_status(sid: str):
    """
    Retorna el estado actual de la sesión de onboarding.
    """
    session = _get(_session_key(sid))
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada o expirada.",
        )
    completados = session.get("pasos_completados", [])
    progreso = int((len(completados) / len(PASOS_ORDEN)) * 100)
    return StatusResponse(
        session_id=sid,
        paso_actual=session.get("paso_actual", PASOS_ORDEN[0]),
        pasos_completados=completados,
        progreso=progreso,
        datos=session.get("datos", {}),
        completado=session.get("completado", False),
        iniciado_en=session.get("iniciado_en", ""),
    )


@router.post("/complete", response_model=CompleteResponse, summary="Completar onboarding")
def onboarding_complete(body: CompleteRequest):
    """
    Marca la sesión de onboarding como completa y retorna el resumen de configuración.
    Requiere que los pasos empresa, regimen, empleados e integraciones estén completados.
    """
    sid = body.session_id
    session = _get(_session_key(sid))
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada o expirada.",
        )

    if session.get("completado"):
        raise HTTPException(status_code=400, detail="El onboarding ya fue completado anteriormente.")

    completados = set(session.get("pasos_completados", []))
    requeridos = {"empresa", "regimen", "empleados", "integraciones"}
    faltantes = requeridos - completados
    if faltantes:
        raise HTTPException(
            status_code=422,
            detail=f"Faltan completar los siguientes pasos: {sorted(faltantes)}",
        )

    datos = session.get("datos", {})
    empresa = datos.get("empresa", {})
    regimen = datos.get("regimen", {})
    empleados = datos.get("empleados", {})
    integraciones = datos.get("integraciones", {})

    # Construir resumen
    resumen = {
        "empresa": {
            "rfc": empresa.get("rfc", "").upper(),
            "nombre": empresa.get("nombre_empresa", ""),
            "giro": empresa.get("giro", ""),
        },
        "fiscal": {
            "regimen": regimen.get("regimen_fiscal", ""),
        },
        "operacion": {
            "rango_empleados": empleados.get("rango_empleados", ""),
        },
        "modulos_activos": integraciones.get("modulos", []),
        "completado_en": datetime.utcnow().isoformat(),
    }

    # Marcar sesión como completa
    session["completado"] = True
    session["completado_en"] = resumen["completado_en"]
    session["resumen"] = resumen
    _set(_session_key(sid), session)

    logger.info(f"Onboarding completado: session_id={sid}, empresa={resumen['empresa']['rfc']}")
    return CompleteResponse(
        session_id=sid,
        completado=True,
        resumen=resumen,
        mensaje=f"¡Bienvenido a Hermes! La configuración de {resumen['empresa']['nombre']} ha sido guardada.",
    )
