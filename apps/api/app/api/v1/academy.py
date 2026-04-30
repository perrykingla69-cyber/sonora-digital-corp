"""
ABE Music Academy — Gamificación completa para artistas
Niveles, XP, logros, misiones, leaderboard, concursos
"""

from __future__ import annotations

from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_tenant_session, get_db
from app.core.deps import get_current_user, CurrentUser
from app.api.v1.academy_logic import (
    RANGOS, LOGROS_TEMPLATE, MISIONES_TEMPLATE,
    xp_para_nivel, nivel_desde_xp, rango_desde_xp,
)

router = APIRouter(prefix="/academy", tags=["ABE Academy"])


async def _get_user_email(user_id: UUID) -> str:
    from sqlalchemy import text
    async with get_db() as db:
        result = await db.execute(
            text("SELECT email FROM users WHERE id = :uid LIMIT 1"),
            {"uid": str(user_id)}
        )
        row = result.fetchone()
        return row.email if row else ""


async def _get_user_xp(email: str) -> int:
    from sqlalchemy import text
    async with get_db() as db:
        result = await db.execute(
            text("""
                SELECT COALESCE(SUM(xp_earned), 0) AS xp
                FROM academy_inscripciones
                WHERE student_email = :email AND status = 'completed'
            """),
            {"email": email}
        )
        row = result.fetchone()
        return int(row.xp) if row else 0


async def _get_catalogo_count(tenant_id: UUID) -> int:
    from sqlalchemy import text
    async with get_tenant_session(tenant_id) as db:
        result = await db.execute(
            text("SELECT COUNT(*) FROM catalogo_musical cm JOIN artistas a ON cm.artista_id = a.id WHERE a.tenant_id = :tid"),
            {"tid": str(tenant_id)}
        )
        row = result.fetchone()
        return int(row[0]) if row else 0


async def _get_fans_count(tenant_id: UUID) -> int:
    from sqlalchemy import text
    async with get_tenant_session(tenant_id) as db:
        result = await db.execute(
            text("SELECT COUNT(*) FROM artist_fans WHERE tenant_id = :tid"),
            {"tid": str(tenant_id)}
        )
        row = result.fetchone()
        return int(row[0]) if row else 0


# ── Endpoints ─────────────────────────────────────────────────────

@router.get("/perfil")
async def get_perfil(user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    email = await _get_user_email(user.user_id)
    xp = await _get_user_xp(email)
    nivel = nivel_desde_xp(xp)
    xp_floor = xp_para_nivel(nivel - 1) if nivel > 1 else 0
    xp_siguiente = xp_para_nivel(nivel)
    progreso_pct = min(100, max(0, int((xp - xp_floor) / max(1, xp_siguiente - xp_floor) * 100)))
    rango, emoji = rango_desde_xp(xp)
    fans = await _get_fans_count(user.tenant_id)
    catalogo = await _get_catalogo_count(user.tenant_id)

    return {
        "nombre": email.split("@")[0].replace(".", " ").title(),
        "nivel": nivel,
        "experiencia": xp,
        "xp_siguiente_nivel": xp_siguiente,
        "xp_nivel_actual": xp_floor,
        "progreso_pct": progreso_pct,
        "rango": rango,
        "rango_emoji": emoji,
        "streak_dias": 0,
        "misiones_activas": len(MISIONES_TEMPLATE),
        "logros_desbloqueados": (1 if catalogo > 0 else 0) + (1 if fans >= 1 else 0),
        "total_logros": len(LOGROS_TEMPLATE),
        "stats": {"cursos_completados": 0, "fans_totales": fans, "canciones_catalogo": catalogo},
    }


@router.get("/cursos")
async def get_cursos(user: CurrentUser = Depends(get_current_user)) -> list[dict[str, Any]]:
    from sqlalchemy import text
    async with get_tenant_session(user.tenant_id) as db:
        result = await db.execute(
            text("SELECT id, slug, titulo, descripcion, nivel, duracion_horas, precio_mxn FROM academy_cursos WHERE activo = true ORDER BY precio_mxn")
        )
        rows = result.fetchall()

    email = await _get_user_email(user.user_id)
    xp = await _get_user_xp(email)
    nivel_usuario = nivel_desde_xp(xp)

    nivel_req_map = {"basico": 1, "intermedio": 3, "avanzado": 6}
    icono_map = {"Producción": "🎚️", "Mezcla": "🎛️", "Acordeón": "🪗", "Marketing": "📱", "Contratos": "📋", "Distribución": "🌐"}

    return [
        {
            "id": str(row.id),
            "slug": row.slug,
            "titulo": row.titulo,
            "descripcion": row.descripcion or "Curso especializado para artistas de ABE Music",
            "categoria": "musica",
            "nivel_req": nivel_req_map.get(str(row.nivel), 1),
            "xp_total": max(50, int(float(row.precio_mxn or 0) // 10)),
            "duracion_min": (row.duracion_horas or 1) * 60,
            "icono": next((v for k, v in icono_map.items() if k in str(row.titulo)), "🎵"),
            "desbloqueado": nivel_usuario >= nivel_req_map.get(str(row.nivel), 1),
            "progreso_pct": 0,
            "clases_completadas": 0,
            "total_clases": 4,
        }
        for row in rows
    ]


@router.get("/misiones")
async def get_misiones(user: CurrentUser = Depends(get_current_user)) -> list[dict[str, Any]]:
    catalogo = await _get_catalogo_count(user.tenant_id)
    return [
        {
            **m,
            "progreso": min(catalogo, m["objetivo"]) if m["id"] == "m_primera_cancion" else m.get("progreso", 0),
            "progreso_pct": min(100, int(min(catalogo, m["objetivo"]) / max(1, m["objetivo"]) * 100)) if m["id"] == "m_primera_cancion" else 0,
            "completada": (catalogo >= m["objetivo"]) if m["id"] == "m_primera_cancion" else False,
        }
        for m in MISIONES_TEMPLATE
    ]


@router.get("/logros")
async def get_logros(user: CurrentUser = Depends(get_current_user)) -> list[dict[str, Any]]:
    catalogo = await _get_catalogo_count(user.tenant_id)
    fans = await _get_fans_count(user.tenant_id)
    email = await _get_user_email(user.user_id)
    xp = await _get_user_xp(email)

    desbloqueados = set()
    if catalogo > 0:
        desbloqueados.add("primer_track")
    if fans >= 1:
        desbloqueados.add("primer_fan")
    if fans >= 10:
        desbloqueados.add("diez_fans")
    if catalogo >= 10:
        desbloqueados.add("catalogo_10")
    if xp > 0:
        desbloqueados.add("primer_curso")

    return [{**l, "desbloqueado": l["id"] in desbloqueados} for l in LOGROS_TEMPLATE]


@router.get("/leaderboard")
async def get_leaderboard(user: CurrentUser = Depends(get_current_user)) -> list[dict[str, Any]]:
    from sqlalchemy import text
    async with get_tenant_session(user.tenant_id) as db:
        result = await db.execute(
            text("""
                SELECT u.email, COALESCE(SUM(ai.xp_earned), 0) AS xp
                FROM users u
                LEFT JOIN academy_inscripciones ai ON ai.student_email = u.email AND ai.status = 'completed'
                WHERE u.tenant_id = :tid
                GROUP BY u.email ORDER BY xp DESC LIMIT 10
            """),
            {"tid": str(user.tenant_id)}
        )
        rows = result.fetchall()

    return [
        {
            "posicion": i,
            "user_id": row.email.split("@")[0],
            "nivel": nivel_desde_xp(int(row.xp)),
            "experiencia": int(row.xp),
            "rango": rango_desde_xp(int(row.xp))[0],
            "emoji": rango_desde_xp(int(row.xp))[1],
            "streak": 0,
        }
        for i, row in enumerate(rows, 1)
    ]


@router.post("/misiones/{mision_id}/completar")
async def completar_mision(mision_id: str, user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    mision = next((m for m in MISIONES_TEMPLATE if m["id"] == mision_id), None)
    if not mision:
        raise HTTPException(status_code=404, detail="Misión no encontrada")

    email = await _get_user_email(user.user_id)
    xp_ganada = mision["xp_reward"]

    from sqlalchemy import text
    async with get_db() as db:
        await db.execute(
            text("""
                INSERT INTO mdx_ledger (wallet_address, student_email, amount, reason)
                VALUES ('0x0000000000000000000000000000000000000000', :email, :amount, :reason)
            """),
            {"email": email, "amount": xp_ganada, "reason": f"Misión: {mision['titulo']}"},
        )

    xp_total = await _get_user_xp(email) + xp_ganada
    nivel = nivel_desde_xp(xp_total)
    rango, _ = rango_desde_xp(xp_total)
    return {"xp_ganada": xp_ganada, "experiencia": xp_total, "nivel": nivel, "rango": rango}


@router.get("/concursos")
async def get_concursos(user: CurrentUser = Depends(get_current_user)) -> list[dict[str, Any]]:
    return [{
        "id": "c_streams_mayo",
        "titulo": "Battle de Streams — Mayo 2026",
        "descripcion": "El artista con más streams en Mayo gana un mes de distribución premium gratis.",
        "fecha_fin": "2026-05-31T23:59:59",
        "premio": "Distribución Premium 1 mes",
        "participantes": 3,
        "estado": "activo",
        "ganador": None,
    }]


@router.post("/concursos/{concurso_id}/unirse")
async def unirse_concurso(concurso_id: str, user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    return {"ok": True, "mensaje": "¡Te uniste al concurso! Que gane el mejor 🏆"}


@router.get("/stats")
async def get_stats(user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    """Dashboard CEO — métricas agregadas de la plataforma ABE Music."""
    from sqlalchemy import text
    async with get_tenant_session(user.tenant_id) as db:
        r = await db.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM artistas WHERE tenant_id = :tid)                               AS total_artistas,
                (SELECT COUNT(*) FROM catalogo_musical cm
                   JOIN artistas a ON cm.artista_id = a.id WHERE a.tenant_id = :tid)                AS total_canciones,
                (SELECT COUNT(*) FROM artist_fans WHERE tenant_id = :tid)                           AS total_fans,
                (SELECT COUNT(*) FROM artist_contrataciones WHERE tenant_id = :tid)                 AS total_contrataciones,
                (SELECT COUNT(*) FROM artist_contrataciones
                   WHERE tenant_id = :tid AND estado = 'confirmado')                                AS contrataciones_confirmadas,
                (SELECT COALESCE(SUM(precio_acordado), 0) FROM artist_contrataciones
                   WHERE tenant_id = :tid AND estado = 'confirmado')                               AS ingresos_contrataciones,
                (SELECT COUNT(*) FROM academy_inscripciones ai
                   JOIN users u ON ai.student_email = u.email
                   WHERE u.tenant_id = :tid)                                                        AS estudiantes_academy,
                (SELECT COUNT(*) FROM academy_inscripciones ai
                   JOIN users u ON ai.student_email = u.email
                   WHERE u.tenant_id = :tid AND ai.status = 'completed')                           AS cursos_completados
        """), {"tid": str(user.tenant_id)})
        row = r.fetchone()

    # Leaderboard top 3
    async with get_tenant_session(user.tenant_id) as db:
        lb = await db.execute(text("""
            SELECT u.email, COALESCE(SUM(ai.xp_earned), 0) AS xp
            FROM users u
            LEFT JOIN academy_inscripciones ai ON ai.student_email = u.email AND ai.status = 'completed'
            WHERE u.tenant_id = :tid
            GROUP BY u.email ORDER BY xp DESC LIMIT 3
        """), {"tid": str(user.tenant_id)})
        top3 = lb.fetchall()

    # Artistas recientes
    async with get_tenant_session(user.tenant_id) as db:
        art = await db.execute(text("""
            SELECT nombre, genero, status, created_at
            FROM artistas WHERE tenant_id = :tid
            ORDER BY created_at DESC LIMIT 5
        """), {"tid": str(user.tenant_id)})
        artistas_recientes = art.fetchall()

    return {
        "kpis": {
            "total_artistas":            int(row.total_artistas),
            "total_canciones":           int(row.total_canciones),
            "total_fans":                int(row.total_fans),
            "total_contrataciones":      int(row.total_contrataciones),
            "contrataciones_confirmadas":int(row.contrataciones_confirmadas),
            "ingresos_contrataciones":   float(row.ingresos_contrataciones),
            "estudiantes_academy":       int(row.estudiantes_academy),
            "cursos_completados":        int(row.cursos_completados),
        },
        "top_artistas": [
            {
                "posicion": i + 1,
                "nombre": r.email.split("@")[0].title(),
                "xp": int(r.xp),
                "nivel": nivel_desde_xp(int(r.xp)),
                "rango": rango_desde_xp(int(r.xp))[0],
                "emoji": rango_desde_xp(int(r.xp))[1],
            }
            for i, r in enumerate(top3)
        ],
        "artistas_recientes": [
            {
                "nombre": a.nombre,
                "genero": a.genero,
                "status": a.status,
                "desde": a.created_at.strftime("%Y-%m-%d") if a.created_at else None,
            }
            for a in artistas_recientes
        ],
        "concurso_activo": {
            "titulo": "Battle de Streams — Mayo 2026",
            "fecha_fin": "2026-05-31",
            "participantes": int(row.total_artistas),
            "estado": "activo",
        },
    }
