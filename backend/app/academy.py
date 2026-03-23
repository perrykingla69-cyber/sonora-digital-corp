"""
Mystic Academy — Router FastAPI
Endpoints de gamificación para usuarios humanos
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, func
from sqlalchemy.orm import Session
import uuid

from database import Base, engine, get_db
from security import get_current_user

router = APIRouter(prefix="/academy", tags=["academy"])

# ── Modelos SQLAlchemy ────────────────────────────────────────────────────────

class AcademyProfile(Base):
    __tablename__ = "academy_profiles"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = Column(String, nullable=False, unique=True, index=True)
    nivel       = Column(Integer, default=1)
    experiencia = Column(Integer, default=0)
    rango       = Column(String, default="Novato")
    streak_dias = Column(Integer, default=0)
    ultima_actividad = Column(DateTime, default=func.now())
    stat_inteligencia  = Column(Integer, default=10)
    stat_creatividad   = Column(Integer, default=10)
    stat_colaboracion  = Column(Integer, default=10)
    stat_resiliencia   = Column(Integer, default=10)
    stat_velocidad     = Column(Integer, default=10)
    created_at  = Column(DateTime, default=func.now())

class AcademyMision(Base):
    __tablename__ = "academy_misiones"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = Column(String, nullable=False, index=True)
    titulo      = Column(String, nullable=False)
    descripcion = Column(Text, default="")
    tipo        = Column(String, default="diaria")  # diaria, semanal, especial
    xp_reward   = Column(Integer, default=50)
    progreso    = Column(Integer, default=0)
    objetivo    = Column(Integer, default=1)
    completada  = Column(Boolean, default=False)
    created_at  = Column(DateTime, default=func.now())

class AcademyLogro(Base):
    __tablename__ = "academy_logros"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = Column(String, nullable=False, index=True)
    logro_key   = Column(String, nullable=False)
    nombre      = Column(String, nullable=False)
    emoji       = Column(String, default="🏆")
    xp_reward   = Column(Integer, default=100)
    desbloqueado = Column(Boolean, default=False)
    fecha_desbloqueo = Column(DateTime, nullable=True)

# Crear tablas
Base.metadata.create_all(bind=engine)

# ── Schemas Pydantic ──────────────────────────────────────────────────────────

RANGOS = [
    ("Novato",     0,     100,  "🌱"),
    ("Aprendiz",   100,   300,  "🌿"),
    ("Estudiante", 300,   600,  "📚"),
    ("Discípulo",  600,   1000, "🎯"),
    ("Erudito",    1000,  1500, "🧠"),
    ("Maestro",    1500,  2500, "👑"),
    ("Sabio",      2500,  4000, "🔮"),
    ("Legendario", 4000,  999999,"⭐"),
]

MISIONES_SEED = [
    ("Validar 5 CFDIs", "Procesa 5 facturas XML en el módulo de facturas", "diaria", 75, 5),
    ("Conciliar banco", "Realiza una conciliación bancaria", "semanal", 150, 1),
    ("Generar reporte", "Descarga un reporte del sistema", "diaria", 50, 1),
    ("Usar Brain IA", "Haz 3 consultas al Brain IA", "diaria", 60, 3),
    ("Cierre mensual", "Completa el cierre de un mes", "semanal", 300, 1),
]

LOGROS_SEED = [
    ("primera_factura", "Primera Factura", "🧾", 50),
    ("racha_7dias",     "Racha de 7 días",  "🔥", 300),
    ("maestro_cfdi",    "Maestro CFDI",     "📄", 200),
    ("cerebro_ia",      "Cerebro IA",       "🧠", 150),
    ("cierre_perfecto", "Cierre Perfecto",  "✅", 400),
]

def _get_rango(xp: int):
    for nombre, mn, mx, emoji in RANGOS:
        if mn <= xp < mx:
            return nombre, emoji
    return "Legendario", "⭐"

def _xp_siguiente_nivel(nivel: int) -> int:
    return int(100 * (1.5 ** (nivel - 1)))

def _ensure_profile(user_id: str, db: Session) -> AcademyProfile:
    p = db.query(AcademyProfile).filter(AcademyProfile.user_id == user_id).first()
    if not p:
        p = AcademyProfile(user_id=user_id)
        db.add(p)
        # Seed misiones
        for titulo, desc, tipo, xp, obj in MISIONES_SEED:
            m = AcademyMision(user_id=user_id, titulo=titulo,
                              descripcion=desc, tipo=tipo, xp_reward=xp, objetivo=obj)
            db.add(m)
        # Seed logros
        for key, nombre, emoji, xp in LOGROS_SEED:
            l = AcademyLogro(user_id=user_id, logro_key=key,
                             nombre=nombre, emoji=emoji, xp_reward=xp)
            db.add(l)
        db.commit()
        db.refresh(p)
    return p

# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/perfil")
def get_perfil(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    p = _ensure_profile(current_user.id, db)
    rango_nombre, rango_emoji = _get_rango(p.experiencia)
    xp_next = _xp_siguiente_nivel(p.nivel)
    misiones_activas = db.query(AcademyMision).filter(
        AcademyMision.user_id == current_user.id,
        AcademyMision.completada == False
    ).count()
    logros = db.query(AcademyLogro).filter(
        AcademyLogro.user_id == current_user.id,
        AcademyLogro.desbloqueado == True
    ).count()
    return {
        "user_id": current_user.id,
        "nombre": current_user.nombre,
        "nivel": p.nivel,
        "experiencia": p.experiencia,
        "xp_siguiente_nivel": xp_next,
        "progreso_pct": round(min(100, (p.experiencia / xp_next) * 100), 1),
        "rango": rango_nombre,
        "rango_emoji": rango_emoji,
        "streak_dias": p.streak_dias,
        "misiones_activas": misiones_activas,
        "logros_desbloqueados": logros,
        "stats": {
            "inteligencia": p.stat_inteligencia,
            "creatividad": p.stat_creatividad,
            "colaboracion": p.stat_colaboracion,
            "resiliencia": p.stat_resiliencia,
            "velocidad": p.stat_velocidad,
        }
    }

@router.get("/misiones")
def get_misiones(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _ensure_profile(current_user.id, db)
    misiones = db.query(AcademyMision).filter(
        AcademyMision.user_id == current_user.id
    ).all()
    return [
        {
            "id": m.id,
            "titulo": m.titulo,
            "descripcion": m.descripcion,
            "tipo": m.tipo,
            "xp_reward": m.xp_reward,
            "progreso": m.progreso,
            "objetivo": m.objetivo,
            "progreso_pct": round(min(100, (m.progreso / m.objetivo) * 100), 1),
            "completada": m.completada,
        }
        for m in misiones
    ]

@router.post("/misiones/{mision_id}/completar")
def completar_mision(
    mision_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    mision = db.query(AcademyMision).filter(
        AcademyMision.id == mision_id,
        AcademyMision.user_id == current_user.id
    ).first()
    if not mision:
        raise HTTPException(404, "Misión no encontrada")
    if mision.completada:
        raise HTTPException(400, "Misión ya completada")

    mision.progreso = mision.objetivo
    mision.completada = True

    # Dar XP
    p = _ensure_profile(current_user.id, db)
    p.experiencia += mision.xp_reward
    # Subir nivel si corresponde
    while p.experiencia >= _xp_siguiente_nivel(p.nivel):
        p.nivel += 1
    # Actualizar rango
    p.rango, _ = _get_rango(p.experiencia)
    p.ultima_actividad = datetime.now()

    db.commit()
    return {
        "ok": True,
        "xp_ganada": mision.xp_reward,
        "nivel_actual": p.nivel,
        "experiencia": p.experiencia,
        "rango": p.rango,
    }

@router.get("/logros")
def get_logros(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _ensure_profile(current_user.id, db)
    logros = db.query(AcademyLogro).filter(
        AcademyLogro.user_id == current_user.id
    ).all()
    return [
        {
            "id": l.id,
            "key": l.logro_key,
            "nombre": l.nombre,
            "emoji": l.emoji,
            "xp_reward": l.xp_reward,
            "desbloqueado": l.desbloqueado,
            "fecha": l.fecha_desbloqueo.isoformat() if l.fecha_desbloqueo else None,
        }
        for l in logros
    ]

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    top = db.query(AcademyProfile).order_by(
        AcademyProfile.nivel.desc(),
        AcademyProfile.experiencia.desc()
    ).limit(10).all()
    result = []
    for i, p in enumerate(top):
        rango_nombre, rango_emoji = _get_rango(p.experiencia)
        result.append({
            "posicion": i + 1,
            "user_id": p.user_id,
            "nivel": p.nivel,
            "experiencia": p.experiencia,
            "rango": rango_nombre,
            "emoji": rango_emoji,
            "streak": p.streak_dias,
        })
    return result

@router.post("/xp/otorgar")
def otorgar_xp(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Endpoint interno: otorga XP por acciones en el dashboard"""
    cantidad = int(payload.get("cantidad", 10))
    razon = payload.get("razon", "acción en dashboard")
    p = _ensure_profile(current_user.id, db)
    p.experiencia += cantidad
    while p.experiencia >= _xp_siguiente_nivel(p.nivel):
        p.nivel += 1
    p.rango, _ = _get_rango(p.experiencia)
    p.ultima_actividad = datetime.now()
    db.commit()
    return {"ok": True, "xp_total": p.experiencia, "nivel": p.nivel, "razon": razon}
