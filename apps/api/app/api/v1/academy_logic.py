"""
ABE Music Academy — lógica pura (sin dependencias de framework).
Importable desde tests sin necesitar FastAPI/Pydantic.
"""
from __future__ import annotations

RANGOS = [
    (0,     "Artista Emergente",      "🌱"),
    (500,   "Voz Local",              "🎵"),
    (2500,  "Sonido Regional",        "🎤"),
    (8000,  "Estrella Nacional",      "⭐"),
    (20000, "Leyenda Internacional",  "🏆"),
]

LOGROS_TEMPLATE = [
    {"id": "primer_track",    "nombre": "Primer Track",         "emoji": "🎸", "xp_reward": 100},
    {"id": "perfil_completo", "nombre": "Perfil Completo",      "emoji": "🎯", "xp_reward": 150},
    {"id": "racha_7",         "nombre": "Racha 7 Días",         "emoji": "🔥", "xp_reward": 200},
    {"id": "primer_fan",      "nombre": "Primer Fan",           "emoji": "👥", "xp_reward": 75},
    {"id": "diez_fans",       "nombre": "10 Fans",              "emoji": "🤩", "xp_reward": 250},
    {"id": "primer_curso",    "nombre": "Primer Curso ABE",     "emoji": "🎓", "xp_reward": 300},
    {"id": "primera_contrat", "nombre": "Primera Contratación", "emoji": "🤝", "xp_reward": 500},
    {"id": "mil_streams",     "nombre": "1K Streams",           "emoji": "📊", "xp_reward": 400},
    {"id": "primer_ingreso",  "nombre": "Primer Ingreso",       "emoji": "💰", "xp_reward": 350},
    {"id": "catalogo_10",     "nombre": "Catálogo 10",          "emoji": "🎵", "xp_reward": 300},
    {"id": "internacional",   "nombre": "Internacional",        "emoji": "🌎", "xp_reward": 600},
    {"id": "certificado_abe", "nombre": "Certificado ABE",      "emoji": "🏅", "xp_reward": 1000},
]

MISIONES_TEMPLATE = [
    {"id": "m_perfil",          "titulo": "Completa tu perfil",          "tipo": "especial",
     "descripcion": "Agrega foto, bio, géneros y redes sociales",        "xp_reward": 150, "objetivo": 1},
    {"id": "m_primera_cancion", "titulo": "Sube tu primera canción",     "tipo": "especial",
     "descripcion": "Agrega al menos una canción a tu catálogo",          "xp_reward": 100, "objetivo": 1},
    {"id": "m_curso_diario",    "titulo": "Estudia hoy en ABE Academy",  "tipo": "diaria",
     "descripcion": "Completa al menos una clase hoy",                   "xp_reward": 50,  "objetivo": 1},
    {"id": "m_semana_contenido","titulo": "Publica contenido esta semana","tipo": "semanal",
     "descripcion": "Comparte una actualización con tus fans",            "xp_reward": 120, "objetivo": 1},
    {"id": "m_streams_semana",  "titulo": "100 streams esta semana",     "tipo": "semanal",
     "descripcion": "Acumula 100 reproducciones en cualquier plataforma","xp_reward": 200, "objetivo": 100},
]


def xp_para_nivel(nivel: int) -> int:
    return int(100 * (nivel ** 1.6))


def nivel_desde_xp(xp: int) -> int:
    n = 1
    while xp >= xp_para_nivel(n):
        n += 1
    return max(n - 1, 1)


def rango_desde_xp(xp: int) -> tuple[str, str]:
    rango, emoji = RANGOS[0][1], RANGOS[0][2]
    for threshold, nombre, em in RANGOS:
        if xp >= threshold:
            rango, emoji = nombre, em
    return rango, emoji
