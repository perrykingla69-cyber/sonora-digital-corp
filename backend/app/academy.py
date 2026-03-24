"""
Mystic Academy — Router FastAPI completo
Cursos, módulos, clases, temas, gamificación, videos híbridos
Inclusivo: lecturas, videos, ejercicios, badges, progreso adaptativo
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import (Column, String, Integer, Float, Boolean,
                        DateTime, Text, ForeignKey, func)
from sqlalchemy.orm import Session
import uuid, json

from database import Base, engine, get_db
from security import get_current_user

router = APIRouter(prefix="/academy", tags=["academy"])

# ══════════════════════════════════════════════════════════════════════════════
# MODELOS
# ══════════════════════════════════════════════════════════════════════════════

class AcademyProfile(Base):
    __tablename__ = "academy_profiles"
    id               = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id          = Column(String, nullable=False, unique=True, index=True)
    nivel            = Column(Integer, default=1)
    experiencia      = Column(Integer, default=0)
    rango            = Column(String, default="Novato")
    streak_dias      = Column(Integer, default=0)
    ultima_actividad = Column(DateTime, default=func.now())
    stat_inteligencia  = Column(Integer, default=10)
    stat_creatividad   = Column(Integer, default=10)
    stat_colaboracion  = Column(Integer, default=10)
    stat_resiliencia   = Column(Integer, default=10)
    stat_velocidad     = Column(Integer, default=10)
    created_at       = Column(DateTime, default=func.now())

class AcademyCurso(Base):
    __tablename__ = "academy_cursos"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    slug        = Column(String, unique=True, nullable=False)
    titulo      = Column(String, nullable=False)
    descripcion = Column(Text, default="")
    categoria   = Column(String, default="contabilidad")  # contabilidad, fiscal, tecnologia, soft_skills
    nivel_req   = Column(Integer, default=1)              # nivel mínimo para acceder
    xp_total    = Column(Integer, default=500)
    duracion_min= Column(Integer, default=120)            # minutos estimados
    icono       = Column(String, default="📚")
    activo      = Column(Boolean, default=True)
    orden       = Column(Integer, default=0)

class AcademyModulo(Base):
    __tablename__ = "academy_modulos"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    curso_id    = Column(String, ForeignKey("academy_cursos.id"), nullable=False)
    titulo      = Column(String, nullable=False)
    descripcion = Column(Text, default="")
    orden       = Column(Integer, default=0)
    xp_reward   = Column(Integer, default=100)

class AcademyClase(Base):
    __tablename__ = "academy_clases"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    modulo_id    = Column(String, ForeignKey("academy_modulos.id"), nullable=False)
    titulo       = Column(String, nullable=False)
    tipo         = Column(String, default="video")  # video, lectura, ejercicio, quiz, hibrido
    contenido    = Column(Text, default="")         # markdown o URL
    video_url    = Column(String, nullable=True)    # URL video externo/CDN
    duracion_min = Column(Integer, default=10)
    xp_reward    = Column(Integer, default=25)
    orden        = Column(Integer, default=0)
    accesible    = Column(Boolean, default=True)    # inclusivo: true por defecto

class AcademyProgreso(Base):
    __tablename__ = "academy_progreso"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = Column(String, nullable=False, index=True)
    clase_id    = Column(String, ForeignKey("academy_clases.id"), nullable=False)
    completada  = Column(Boolean, default=False)
    pct         = Column(Integer, default=0)        # 0-100 porcentaje visto/leído
    notas       = Column(Text, default="")
    completada_at = Column(DateTime, nullable=True)

class AcademyMision(Base):
    __tablename__ = "academy_misiones"
    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id     = Column(String, nullable=False, index=True)
    titulo      = Column(String, nullable=False)
    descripcion = Column(Text, default="")
    tipo        = Column(String, default="diaria")
    xp_reward   = Column(Integer, default=50)
    progreso    = Column(Integer, default=0)
    objetivo    = Column(Integer, default=1)
    completada  = Column(Boolean, default=False)
    created_at  = Column(DateTime, default=func.now())

class AcademyLogro(Base):
    __tablename__ = "academy_logros"
    id               = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id          = Column(String, nullable=False, index=True)
    logro_key        = Column(String, nullable=False)
    nombre           = Column(String, nullable=False)
    emoji            = Column(String, default="🏆")
    xp_reward        = Column(Integer, default=100)
    desbloqueado     = Column(Boolean, default=False)
    fecha_desbloqueo = Column(DateTime, nullable=True)

Base.metadata.create_all(bind=engine)

# ══════════════════════════════════════════════════════════════════════════════
# CATÁLOGO DE CURSOS (seed data completo)
# ══════════════════════════════════════════════════════════════════════════════

CURSOS_CATALOG = [
  {
    "slug": "contabilidad-basica",
    "titulo": "Contabilidad Básica para PYMEs",
    "descripcion": "Fundamentos de contabilidad: registros, estados financieros y control.",
    "categoria": "contabilidad", "nivel_req": 1, "xp_total": 500,
    "duracion_min": 180, "icono": "📊", "orden": 1,
    "modulos": [
      {
        "titulo": "Introducción a la Contabilidad",
        "orden": 1, "xp_reward": 100,
        "clases": [
          {"titulo": "¿Qué es la contabilidad?", "tipo": "video",
           "video_url": "https://www.youtube.com/embed/placeholder1",
           "contenido": "# ¿Qué es la contabilidad?\nLa contabilidad registra, clasifica y resume transacciones financieras...",
           "duracion_min": 8, "xp_reward": 20, "orden": 1},
          {"titulo": "Principios contables básicos", "tipo": "lectura",
           "contenido": "# Principios Contables\n\n## 1. Entidad\nLa empresa es independiente de sus dueños...\n\n## 2. Negocio en marcha\nSe asume que la empresa continuará operando...\n\n## 3. Periodo contable\nLa actividad se divide en periodos iguales (mensual, anual).",
           "duracion_min": 12, "xp_reward": 20, "orden": 2},
          {"titulo": "El Balance General", "tipo": "hibrido",
           "video_url": "https://www.youtube.com/embed/placeholder2",
           "contenido": "## Balance General\n**Activo = Pasivo + Capital**\n\nEjercicio: clasifica estas cuentas...",
           "duracion_min": 15, "xp_reward": 30, "orden": 3},
          {"titulo": "Quiz: Conceptos básicos", "tipo": "quiz",
           "contenido": json.dumps([
             {"pregunta": "¿Qué registra la contabilidad?", "opciones": ["Solo gastos","Todas las transacciones","Solo ingresos","Solo impuestos"], "correcta": 1},
             {"pregunta": "Activo = Pasivo + ?", "opciones": ["Deudas","Capital","Ventas","Gastos"], "correcta": 1},
           ]), "duracion_min": 5, "xp_reward": 30, "orden": 4},
        ]
      },
      {
        "titulo": "Estados Financieros",
        "orden": 2, "xp_reward": 150,
        "clases": [
          {"titulo": "Estado de Resultados", "tipo": "video",
           "video_url": "https://www.youtube.com/embed/placeholder3",
           "contenido": "# Estado de Resultados\nIngresos - Costos - Gastos = Utilidad Neta",
           "duracion_min": 10, "xp_reward": 25, "orden": 1},
          {"titulo": "Flujo de Efectivo", "tipo": "hibrido",
           "contenido": "## Flujo de Caja\nOperación + Inversión + Financiamiento",
           "duracion_min": 12, "xp_reward": 25, "orden": 2},
          {"titulo": "Lectura de estados financieros", "tipo": "ejercicio",
           "contenido": "### Ejercicio práctico\nAnaliza los estados financieros de 'Empresa Ejemplo S.A. de C.V.'...",
           "duracion_min": 20, "xp_reward": 50, "orden": 3},
        ]
      },
      {
        "titulo": "Control Interno",
        "orden": 3, "xp_reward": 100,
        "clases": [
          {"titulo": "Conciliación bancaria", "tipo": "video",
           "video_url": "https://www.youtube.com/embed/placeholder4",
           "contenido": "# Conciliación Bancaria\nComparar saldo libro vs saldo banco.",
           "duracion_min": 10, "xp_reward": 30, "orden": 1},
          {"titulo": "Depreciación de activos", "tipo": "lectura",
           "contenido": "# Depreciación\n## Método de línea recta\n`Dep = (Costo - Valor residual) / Vida útil`",
           "duracion_min": 10, "xp_reward": 30, "orden": 2},
          {"titulo": "Quiz final: Control", "tipo": "quiz",
           "contenido": json.dumps([
             {"pregunta": "¿Para qué sirve la conciliación bancaria?", "opciones": ["Calcular impuestos","Comparar saldos banco vs libros","Emitir facturas","Nada"], "correcta": 1},
           ]), "duracion_min": 5, "xp_reward": 40, "orden": 3},
        ]
      },
    ]
  },
  {
    "slug": "cfdi-40-practico",
    "titulo": "CFDI 4.0 Práctico",
    "descripcion": "Facturación electrónica con CFDI 4.0: tipos, complementos y cancelaciones.",
    "categoria": "fiscal", "nivel_req": 1, "xp_total": 400,
    "duracion_min": 150, "icono": "🧾", "orden": 2,
    "modulos": [
      {
        "titulo": "Fundamentos CFDI 4.0",
        "orden": 1, "xp_reward": 120,
        "clases": [
          {"titulo": "¿Qué cambió en CFDI 4.0?", "tipo": "video",
           "contenido": "# CFDI 4.0 vs 3.3\nCambios principales: RFC receptor obligatorio, uso del CFDI, exportación...",
           "duracion_min": 12, "xp_reward": 30, "orden": 1},
          {"titulo": "Catálogos SAT 2026", "tipo": "lectura",
           "contenido": "## Catálogos clave\n- **c_UsoCFDI**: G01 Adquisición de mercancias, P01 Por definir...\n- **c_RegimenFiscal**: 601 General PF, 621 RESICO...\n- **c_FormaPago**: 01 Efectivo, 03 Transferencia...",
           "duracion_min": 15, "xp_reward": 30, "orden": 2},
          {"titulo": "Tipos de CFDI", "tipo": "hibrido",
           "contenido": "## Tipos\n- **I** Ingreso\n- **E** Egreso (nota crédito)\n- **T** Traslado\n- **N** Nómina\n- **P** Pago (REP)",
           "duracion_min": 10, "xp_reward": 30, "orden": 3},
          {"titulo": "Quiz CFDI 4.0", "tipo": "quiz",
           "contenido": json.dumps([
             {"pregunta": "¿Cuál es el uso de CFDI para gastos generales?", "opciones": ["G01","G03","P01","CN01"], "correcta": 1},
             {"pregunta": "¿Qué tipo de CFDI es una nota de crédito?", "opciones": ["I","E","T","P"], "correcta": 1},
           ]), "duracion_min": 5, "xp_reward": 30, "orden": 4},
        ]
      },
      {
        "titulo": "Complementos y Cancelaciones",
        "orden": 2, "xp_reward": 140,
        "clases": [
          {"titulo": "Complemento de Pago (REP)", "tipo": "video",
           "contenido": "# REP — Recibo Electrónico de Pago\nCuándo y cómo emitirlo correctamente.",
           "duracion_min": 15, "xp_reward": 40, "orden": 1},
          {"titulo": "Cancelación de CFDI", "tipo": "hibrido",
           "contenido": "## Motivos de cancelación\n01 - Comprobante emitido con errores con relación\n02 - Sin relación\n03 - No se llevó a cabo la operación\n04 - Nominativa",
           "duracion_min": 12, "xp_reward": 40, "orden": 2},
          {"titulo": "Ejercicio: emitir en Mystic", "tipo": "ejercicio",
           "contenido": "### Practica en el sistema\nVe a **Facturas → Nueva Factura** y emite una factura de prueba.",
           "duracion_min": 15, "xp_reward": 60, "orden": 3},
        ]
      },
    ]
  },
  {
    "slug": "resico-pf-2026",
    "titulo": "RESICO PF 2026",
    "descripcion": "Régimen Simplificado de Confianza para Personas Físicas: declaraciones, tasas y límites.",
    "categoria": "fiscal", "nivel_req": 2, "xp_total": 350,
    "duracion_min": 120, "icono": "💼", "orden": 3,
    "modulos": [
      {
        "titulo": "¿Qué es RESICO?",
        "orden": 1, "xp_reward": 100,
        "clases": [
          {"titulo": "RESICO vs Régimen General", "tipo": "video",
           "contenido": "# RESICO\nArt. 113-E al 113-J LISR. Tasa 1%-2.5% sobre ingresos efectivamente cobrados.",
           "duracion_min": 12, "xp_reward": 30, "orden": 1},
          {"titulo": "Límite de ingresos y tasas", "tipo": "lectura",
           "contenido": "## Tasas RESICO 2026\n| Ingreso anual | Tasa |\n|---|---|\n| Hasta $300,000 | 1.0% |\n| $300,001 - $600,000 | 1.1% |\n| $600,001 - $1,000,000 | 1.5% |\n| $1,000,001 - $2,000,000 | 2.0% |\n| $2,000,001 - $3,500,000 | 2.5% |",
           "duracion_min": 10, "xp_reward": 30, "orden": 2},
          {"titulo": "Obligaciones del RESICO", "tipo": "hibrido",
           "contenido": "## Lo que debes hacer:\n1. Emitir CFDI 4.0 por todos los ingresos\n2. Pago provisional mensual (día 17)\n3. Declaración anual (abril)\n4. Conservar comprobantes 5 años",
           "duracion_min": 10, "xp_reward": 40, "orden": 3},
        ]
      },
      {
        "titulo": "Pagos y Declaraciones",
        "orden": 2, "xp_reward": 150,
        "clases": [
          {"titulo": "Cálculo del pago mensual", "tipo": "ejercicio",
           "contenido": "### Ejercicio\nTus ingresos de enero fueron $45,000. ¿Cuánto pagas de ISR RESICO?\n\n**Solución:** $45,000 × 1.0% = **$450**",
           "duracion_min": 15, "xp_reward": 50, "orden": 1},
          {"titulo": "Retenciones de ISR (1.25%)", "tipo": "video",
           "contenido": "# Retenciones\nCuando una Persona Moral te paga, retiene el 1.25% de ISR (Art. 113-J LISR).",
           "duracion_min": 10, "xp_reward": 40, "orden": 2},
          {"titulo": "Quiz RESICO final", "tipo": "quiz",
           "contenido": json.dumps([
             {"pregunta": "¿Cuánto pagas de ISR RESICO con ingresos de $200,000?", "opciones": ["$2,000","$3,000","$4,000","$1,000"], "correcta": 0},
             {"pregunta": "¿Cuál es la tasa máxima del RESICO?", "opciones": ["1%","2.5%","3.5%","5%"], "correcta": 1},
           ]), "duracion_min": 5, "xp_reward": 60, "orden": 3},
        ]
      },
    ]
  },
  {
    "slug": "nomina-imss-2026",
    "titulo": "Nómina e IMSS 2026",
    "descripcion": "Cálculo correcto de nómina, cuotas IMSS, INFONAVIT y timbrado.",
    "categoria": "contabilidad", "nivel_req": 2, "xp_total": 400,
    "duracion_min": 150, "icono": "👥", "orden": 4,
    "modulos": [
      {
        "titulo": "Estructura de la Nómina",
        "orden": 1, "xp_reward": 130,
        "clases": [
          {"titulo": "Componentes del salario", "tipo": "video",
           "contenido": "# Salario\n- Salario base\n- Partes proporcionales: aguinaldo (15 días), vacaciones, prima vacacional 25%\n- Salario Diario Integrado (SDI)",
           "duracion_min": 12, "xp_reward": 35, "orden": 1},
          {"titulo": "Cuotas IMSS 2026", "tipo": "lectura",
           "contenido": "## IMSS Trabajador 2026\n| Concepto | % |\n|---|---|\n| Enf. Mat. cuota fija | 0.40% sobre 3 UMA |\n| Enf. Mat. excedente | 0.40% sobre excedente |\n| Invalidez y vida | 0.625% |\n| Cesantía y vejez | 1.125% |\n\n**UMA 2026:** $108.57 diario / $3,300.53 mensual",
           "duracion_min": 15, "xp_reward": 35, "orden": 2},
          {"titulo": "INFONAVIT y retenciones", "tipo": "hibrido",
           "contenido": "## INFONAVIT\nAportación patrón: 5% del SDI\nDescuento trabajador: según crédito otorgado (VSM o fijo)\n\n## ISR nómina\nUsamos tabla Art. 96 LISR con subsidio al empleo.",
           "duracion_min": 12, "xp_reward": 30, "orden": 3},
          {"titulo": "Ejercicio: calcular nómina", "tipo": "ejercicio",
           "contenido": "### Caso práctico\nEmpleado con salario mensual $12,000:\n1. Calcula SDI (incluye partes proporcionales)\n2. Calcula IMSS trabajador\n3. Calcula ISR con tabla\n4. Determina neto a pagar",
           "duracion_min": 20, "xp_reward": 30, "orden": 4},
        ]
      },
      {
        "titulo": "CFDI de Nómina",
        "orden": 2, "xp_reward": 120,
        "clases": [
          {"titulo": "Timbrado de recibos", "tipo": "video",
           "contenido": "# CFDI Nómina (tipo N)\nObligatorio desde 2014. Complemento de nómina versión 1.2.",
           "duracion_min": 12, "xp_reward": 40, "orden": 1},
          {"titulo": "Errores comunes", "tipo": "lectura",
           "contenido": "## Errores frecuentes en CFDI nómina:\n1. Tipo de percepción incorrecto (001 vs 019)\n2. SDI mal calculado\n3. Días trabajados incorrectos\n4. Registro patronal inválido",
           "duracion_min": 10, "xp_reward": 40, "orden": 2},
          {"titulo": "Quiz nómina", "tipo": "quiz",
           "contenido": json.dumps([
             {"pregunta": "¿Cuántos días de aguinaldo marca la LFT como mínimo?", "opciones": ["10","15","20","30"], "correcta": 1},
             {"pregunta": "¿Qué porcentaje es la prima vacacional mínima?", "opciones": ["15%","20%","25%","30%"], "correcta": 2},
           ]), "duracion_min": 5, "xp_reward": 40, "orden": 3},
        ]
      },
    ]
  },
  {
    "slug": "mystic-plataforma",
    "titulo": "Domina la Plataforma Mystic",
    "descripcion": "Aprende a usar todas las funciones de Mystic: Brain IA, facturas, reportes y automatizaciones.",
    "categoria": "tecnologia", "nivel_req": 1, "xp_total": 300,
    "duracion_min": 90, "icono": "🤖", "orden": 5,
    "modulos": [
      {
        "titulo": "Brain IA",
        "orden": 1, "xp_reward": 100,
        "clases": [
          {"titulo": "¿Qué puede hacer el Brain?", "tipo": "video",
           "contenido": "# Brain IA\nConsulta fiscal, generación de reportes, análisis de CFDIs y más.",
           "duracion_min": 8, "xp_reward": 25, "orden": 1},
          {"titulo": "Prompts efectivos para contabilidad", "tipo": "lectura",
           "contenido": "## Cómo preguntarle al Brain\n- ¿Cuánto IVA acumulé en enero?\n- Resume mi estado de resultados de Q1 2026\n- ¿Qué facturas están pendientes de cobro?\n- Calcula el ISR mensual con ingreso de $X",
           "duracion_min": 10, "xp_reward": 25, "orden": 2},
          {"titulo": "Ejercicio: 3 consultas al Brain", "tipo": "ejercicio",
           "contenido": "### Practica ahora\nVe a **Brain IA** y realiza estas 3 consultas:\n1. 'Dame el resumen del mes actual'\n2. 'Lista facturas pendientes'\n3. Una pregunta fiscal de tu elección",
           "duracion_min": 15, "xp_reward": 50, "orden": 3},
        ]
      },
      {
        "titulo": "Automatizaciones N8N",
        "orden": 2, "xp_reward": 100,
        "clases": [
          {"titulo": "¿Qué es N8N?", "tipo": "video",
           "contenido": "# N8N — Automatización sin código\nConecta sistemas: WhatsApp → Mystic → SAT → Notificaciones.",
           "duracion_min": 10, "xp_reward": 30, "orden": 1},
          {"titulo": "Workflows disponibles", "tipo": "lectura",
           "contenido": "## Flows activos en Mystic\n- Alerta CFDI vencido → WhatsApp\n- Recordatorio declaración SAT → Telegram\n- Ingreso nuevo → Registro automático\n- Conciliación bancaria diaria",
           "duracion_min": 10, "xp_reward": 30, "orden": 2},
          {"titulo": "Quiz plataforma", "tipo": "quiz",
           "contenido": json.dumps([
             {"pregunta": "¿Desde dónde consultas el Brain IA?", "opciones": ["/facturas","/brain","/dashboard","/admin"], "correcta": 1},
             {"pregunta": "¿Qué herramienta automatiza workflows en Mystic?", "opciones": ["Python","N8N","Excel","Telegram"], "correcta": 1},
           ]), "duracion_min": 5, "xp_reward": 40, "orden": 3},
        ]
      },
    ]
  },
]

MISIONES_SEED = [
    ("Validar 5 CFDIs",       "Procesa 5 facturas XML en el módulo de facturas",  "diaria",   75, 5),
    ("Conciliar banco",       "Realiza una conciliación bancaria",                 "semanal", 150, 1),
    ("Completar una clase",   "Termina cualquier clase en la Academy",             "diaria",   60, 1),
    ("Usar Brain IA 3 veces", "Haz 3 consultas al Brain IA",                       "diaria",   60, 3),
    ("Cierre mensual",        "Completa el cierre de un mes",                      "semanal", 300, 1),
    ("Descargar reporte",     "Genera y descarga un reporte del sistema",          "semanal",  80, 1),
    ("Racha de 3 días",       "Ingresa 3 días seguidos a la plataforma",           "especial", 200, 3),
]

LOGROS_SEED = [
    ("primera_clase",   "Primera Clase",     "🎓", 50),
    ("cfdi_experto",    "Experto en CFDI",   "🧾", 200),
    ("racha_7dias",     "Racha de 7 días",   "🔥", 300),
    ("resico_master",   "RESICO Master",     "💼", 250),
    ("brain_user",      "Cerebro Digital",   "🤖", 150),
    ("nomina_pro",      "Pro de Nómina",     "👥", 200),
    ("curso_completo",  "Curso Completado",  "🏆", 500),
    ("nivel_erudito",   "Erudito",           "🧠", 400),
]

# ══════════════════════════════════════════════════════════════════════════════
# RANGOS / XP
# ══════════════════════════════════════════════════════════════════════════════

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

def _get_rango(xp: int):
    for n, mn, mx, e in RANGOS:
        if mn <= xp < mx:
            return n, e
    return "Legendario", "⭐"

def _xp_siguiente_nivel(nivel: int) -> int:
    return int(100 * (1.5 ** (nivel - 1)))

def _ensure_profile(user_id: str, db: Session) -> AcademyProfile:
    p = db.query(AcademyProfile).filter(AcademyProfile.user_id == user_id).first()
    if not p:
        p = AcademyProfile(user_id=user_id)
        db.add(p)
        for titulo, desc, tipo, xp, obj in MISIONES_SEED:
            db.add(AcademyMision(user_id=user_id, titulo=titulo,
                                 descripcion=desc, tipo=tipo,
                                 xp_reward=xp, objetivo=obj))
        for key, nombre, emoji, xp in LOGROS_SEED:
            db.add(AcademyLogro(user_id=user_id, logro_key=key,
                                nombre=nombre, emoji=emoji, xp_reward=xp))
        db.commit()
        db.refresh(p)
    return p

def _dar_xp(user_id: str, cantidad: int, db: Session) -> AcademyProfile:
    p = _ensure_profile(user_id, db)
    p.experiencia += cantidad
    while p.experiencia >= _xp_siguiente_nivel(p.nivel):
        p.nivel += 1
    p.rango, _ = _get_rango(p.experiencia)
    p.ultima_actividad = datetime.now()
    db.commit()
    return p

def _seed_cursos(db: Session):
    if db.query(AcademyCurso).count() > 0:
        return
    for c in CURSOS_CATALOG:
        curso = AcademyCurso(
            slug=c["slug"], titulo=c["titulo"], descripcion=c["descripcion"],
            categoria=c["categoria"], nivel_req=c["nivel_req"], xp_total=c["xp_total"],
            duracion_min=c["duracion_min"], icono=c["icono"], orden=c["orden"]
        )
        db.add(curso); db.flush()
        for m in c["modulos"]:
            mod = AcademyModulo(curso_id=curso.id, titulo=m["titulo"],
                                orden=m["orden"], xp_reward=m["xp_reward"])
            db.add(mod); db.flush()
            for cl in m["clases"]:
                db.add(AcademyClase(
                    modulo_id=mod.id, titulo=cl["titulo"], tipo=cl["tipo"],
                    contenido=cl.get("contenido",""), video_url=cl.get("video_url"),
                    duracion_min=cl["duracion_min"], xp_reward=cl["xp_reward"],
                    orden=cl["orden"]
                ))
    db.commit()

# ══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/perfil")
def get_perfil(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _seed_cursos(db)
    p = _ensure_profile(current_user.id, db)
    rango_n, rango_e = _get_rango(p.experiencia)
    xp_next = _xp_siguiente_nivel(p.nivel)
    return {
        "user_id": current_user.id,
        "nombre": current_user.nombre,
        "nivel": p.nivel,
        "experiencia": p.experiencia,
        "xp_siguiente_nivel": xp_next,
        "progreso_pct": round(min(100,(p.experiencia/xp_next)*100),1),
        "rango": rango_n, "rango_emoji": rango_e,
        "streak_dias": p.streak_dias,
        "misiones_activas": db.query(AcademyMision).filter(
            AcademyMision.user_id==current_user.id,
            AcademyMision.completada==False).count(),
        "logros_desbloqueados": db.query(AcademyLogro).filter(
            AcademyLogro.user_id==current_user.id,
            AcademyLogro.desbloqueado==True).count(),
        "total_logros": len(LOGROS_SEED),
        "stats": {"inteligencia":p.stat_inteligencia,"creatividad":p.stat_creatividad,
                  "colaboracion":p.stat_colaboracion,"resiliencia":p.stat_resiliencia,
                  "velocidad":p.stat_velocidad},
    }

@router.get("/cursos")
def get_cursos(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _seed_cursos(db)
    p = _ensure_profile(current_user.id, db)
    cursos = db.query(AcademyCurso).filter(AcademyCurso.activo==True).order_by(AcademyCurso.orden).all()
    result = []
    for c in cursos:
        modulos = db.query(AcademyModulo).filter(AcademyModulo.curso_id==c.id).all()
        total_clases = 0
        clases_completadas = 0
        for m in modulos:
            clases = db.query(AcademyClase).filter(AcademyClase.modulo_id==m.id).all()
            for cl in clases:
                total_clases += 1
                prog = db.query(AcademyProgreso).filter(
                    AcademyProgreso.user_id==current_user.id,
                    AcademyProgreso.clase_id==cl.id,
                    AcademyProgreso.completada==True).first()
                if prog: clases_completadas += 1
        pct = round((clases_completadas/total_clases*100) if total_clases else 0, 1)
        result.append({
            "id": c.id, "slug": c.slug, "titulo": c.titulo,
            "descripcion": c.descripcion, "categoria": c.categoria,
            "nivel_req": c.nivel_req, "xp_total": c.xp_total,
            "duracion_min": c.duracion_min, "icono": c.icono,
            "desbloqueado": p.nivel >= c.nivel_req,
            "progreso_pct": pct,
            "clases_completadas": clases_completadas,
            "total_clases": total_clases,
        })
    return result

@router.get("/cursos/{slug}")
def get_curso_detail(slug: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _seed_cursos(db)
    curso = db.query(AcademyCurso).filter(AcademyCurso.slug==slug).first()
    if not curso: raise HTTPException(404, "Curso no encontrado")
    modulos = db.query(AcademyModulo).filter(AcademyModulo.curso_id==curso.id).order_by(AcademyModulo.orden).all()
    mods_data = []
    for m in modulos:
        clases = db.query(AcademyClase).filter(AcademyClase.modulo_id==m.id).order_by(AcademyClase.orden).all()
        clases_data = []
        for cl in clases:
            prog = db.query(AcademyProgreso).filter(
                AcademyProgreso.user_id==current_user.id,
                AcademyProgreso.clase_id==cl.id).first()
            clases_data.append({
                "id": cl.id, "titulo": cl.titulo, "tipo": cl.tipo,
                "duracion_min": cl.duracion_min, "xp_reward": cl.xp_reward,
                "orden": cl.orden, "accesible": cl.accesible,
                "completada": prog.completada if prog else False,
                "progreso_pct": prog.pct if prog else 0,
            })
        mods_data.append({"id": m.id, "titulo": m.titulo, "orden": m.orden,
                          "xp_reward": m.xp_reward, "clases": clases_data})
    return {"id": curso.id, "slug": curso.slug, "titulo": curso.titulo,
            "descripcion": curso.descripcion, "icono": curso.icono,
            "xp_total": curso.xp_total, "duracion_min": curso.duracion_min,
            "modulos": mods_data}

@router.get("/clases/{clase_id}")
def get_clase(clase_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cl = db.query(AcademyClase).filter(AcademyClase.id==clase_id).first()
    if not cl: raise HTTPException(404, "Clase no encontrada")
    prog = db.query(AcademyProgreso).filter(
        AcademyProgreso.user_id==current_user.id,
        AcademyProgreso.clase_id==clase_id).first()
    return {
        "id": cl.id, "titulo": cl.titulo, "tipo": cl.tipo,
        "contenido": cl.contenido, "video_url": cl.video_url,
        "duracion_min": cl.duracion_min, "xp_reward": cl.xp_reward,
        "completada": prog.completada if prog else False,
        "progreso_pct": prog.pct if prog else 0,
        "notas": prog.notas if prog else "",
    }

@router.post("/clases/{clase_id}/completar")
def completar_clase(clase_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cl = db.query(AcademyClase).filter(AcademyClase.id==clase_id).first()
    if not cl: raise HTTPException(404, "Clase no encontrada")
    prog = db.query(AcademyProgreso).filter(
        AcademyProgreso.user_id==current_user.id,
        AcademyProgreso.clase_id==clase_id).first()
    xp_ganada = 0
    if not prog:
        prog = AcademyProgreso(user_id=current_user.id, clase_id=clase_id)
        db.add(prog)
    if not prog.completada:
        prog.completada = True; prog.pct = 100
        prog.completada_at = datetime.now()
        xp_ganada = cl.xp_reward
        p = _dar_xp(current_user.id, xp_ganada, db)
        nivel = p.nivel; rango = p.rango
    else:
        p = _ensure_profile(current_user.id, db)
        nivel = p.nivel; rango = p.rango
    db.commit()
    return {"ok": True, "xp_ganada": xp_ganada, "nivel": nivel, "rango": rango}

@router.post("/clases/{clase_id}/progreso")
def actualizar_progreso(clase_id: str, body: dict,
                        db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    pct = min(100, max(0, int(body.get("pct", 0))))
    notas = body.get("notas", "")
    prog = db.query(AcademyProgreso).filter(
        AcademyProgreso.user_id==current_user.id,
        AcademyProgreso.clase_id==clase_id).first()
    if not prog:
        prog = AcademyProgreso(user_id=current_user.id, clase_id=clase_id)
        db.add(prog)
    prog.pct = pct; prog.notas = notas
    db.commit()
    return {"ok": True, "pct": pct}

@router.get("/misiones")
def get_misiones(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _ensure_profile(current_user.id, db)
    return [{"id":m.id,"titulo":m.titulo,"descripcion":m.descripcion,"tipo":m.tipo,
             "xp_reward":m.xp_reward,"progreso":m.progreso,"objetivo":m.objetivo,
             "progreso_pct":round(min(100,(m.progreso/m.objetivo)*100),1),
             "completada":m.completada}
            for m in db.query(AcademyMision).filter(AcademyMision.user_id==current_user.id).all()]

@router.post("/misiones/{mision_id}/completar")
def completar_mision(mision_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    m = db.query(AcademyMision).filter(
        AcademyMision.id==mision_id, AcademyMision.user_id==current_user.id).first()
    if not m: raise HTTPException(404, "Misión no encontrada")
    if m.completada: raise HTTPException(400, "Ya completada")
    m.progreso = m.objetivo; m.completada = True
    p = _dar_xp(current_user.id, m.xp_reward, db)
    return {"ok":True,"xp_ganada":m.xp_reward,"nivel":p.nivel,"experiencia":p.experiencia,"rango":p.rango}

@router.get("/logros")
def get_logros(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _ensure_profile(current_user.id, db)
    return [{"id":l.id,"key":l.logro_key,"nombre":l.nombre,"emoji":l.emoji,
             "xp_reward":l.xp_reward,"desbloqueado":l.desbloqueado,
             "fecha":l.fecha_desbloqueo.isoformat() if l.fecha_desbloqueo else None}
            for l in db.query(AcademyLogro).filter(AcademyLogro.user_id==current_user.id).all()]

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    top = db.query(AcademyProfile).order_by(
        AcademyProfile.nivel.desc(), AcademyProfile.experiencia.desc()).limit(10).all()
    return [{"posicion":i+1,"user_id":p.user_id,"nivel":p.nivel,"experiencia":p.experiencia,
             "rango":p.rango,"emoji":_get_rango(p.experiencia)[1],"streak":p.streak_dias}
            for i,p in enumerate(top)]

@router.post("/xp/otorgar")
def otorgar_xp(body: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    p = _dar_xp(current_user.id, int(body.get("cantidad",10)), db)
    return {"ok":True,"xp_total":p.experiencia,"nivel":p.nivel,"razon":body.get("razon","")}
