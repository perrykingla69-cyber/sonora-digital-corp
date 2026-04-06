"""
Webhook — HeyGen
Recibe notificaciones de videos terminados (éxito o fallo).
Actualiza tabla `videos` y notifica al usuario por Telegram.
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal

router = APIRouter()
logger = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────

async def _telegram_notify(chat_id: str, html: str) -> None:
    """Envía mensaje Telegram al usuario. Silencia errores para no romper el webhook."""
    token = getattr(settings, "TELEGRAM_TOKEN_HERMES", "")
    if not token or not chat_id:
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": html, "parse_mode": "HTML"},
            )
    except Exception as exc:
        logger.warning("Telegram notify failed: %s", exc)


async def _get_user_chat_id(video_id: str) -> Optional[str]:
    """Busca el telegram_chat_id del dueño del video."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("""
                SELECT u.telegram_chat_id
                FROM videos v
                JOIN users u ON u.id = v.user_id
                WHERE v.external_id = :vid
                LIMIT 1
            """),
            {"vid": video_id},
        )
        row = result.fetchone()
    return row.telegram_chat_id if row else None


# ── Endpoint ─────────────────────────────────────────────────

@router.post("/heygen", status_code=200)
async def heygen_webhook(
    request: Request,
    x_heygen_signature: Optional[str] = Header(None),
):
    """
    Payload esperado de HeyGen:
    {
        "event_type": "avatar_video.success" | "avatar_video.fail",
        "video_id": "abc123",
        "status": "success" | "failed",
        "url": "https://cdn.heygen.com/..."   # solo en success
    }
    """
    # ── Verificar secret ──────────────────────────────────────
    secret = getattr(settings, "HEYGEN_WEBHOOK_SECRET", "")
    if secret and x_heygen_signature != secret:
        logger.warning("HeyGen webhook: firma inválida desde %s", request.client.host)
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload: dict = await request.json()
    video_id: str = payload.get("video_id", "")
    status_val: str = payload.get("status", "")
    video_url: str = payload.get("url", "")

    if not video_id:
        return {"ok": True, "skipped": "no video_id"}

    # ── Actualizar DB ─────────────────────────────────────────
    async with AsyncSessionLocal() as db:
        if status_val == "success":
            await db.execute(
                text("""
                    UPDATE videos
                    SET status = 'ready',
                        url = :url,
                        updated_at = NOW()
                    WHERE external_id = :vid
                """),
                {"url": video_url, "vid": video_id},
            )
            logger.info("Video listo: %s → %s", video_id, video_url)

        elif status_val == "failed":
            error_msg = payload.get("error", "Error desconocido")
            await db.execute(
                text("""
                    UPDATE videos
                    SET status = 'failed',
                        error_message = :err,
                        updated_at = NOW()
                    WHERE external_id = :vid
                """),
                {"err": str(error_msg), "vid": video_id},
            )
            logger.error("Video fallido: %s — %s", video_id, error_msg)

        else:
            logger.info("HeyGen evento ignorado: status=%s video=%s", status_val, video_id)
            return {"ok": True, "skipped": f"status={status_val}"}

        await db.commit()

    # ── Notificar usuario ─────────────────────────────────────
    chat_id = await _get_user_chat_id(video_id)
    if chat_id:
        if status_val == "success":
            msg = (
                "✅ <b>Tu video está listo</b>\n\n"
                f"🎬 <a href='{video_url}'>Ver video</a>\n\n"
                "Puedes descargarlo desde tu panel de HERMES OS."
            )
        else:
            msg = (
                "❌ <b>Error al procesar tu video</b>\n\n"
                f"ID: <code>{video_id}</code>\n"
                "El equipo de soporte fue notificado. Intenta de nuevo en unos minutos."
            )
        await _telegram_notify(chat_id, msg)

    return {"ok": True, "video_id": video_id, "status": status_val}
