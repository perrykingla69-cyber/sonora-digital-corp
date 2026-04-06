"""
Webhook — fal.ai
Recibe notificaciones de imágenes/videos generados.
Guarda URL en tabla `assets`, actualiza tokens consumidos y notifica al usuario.
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


def _extract_output_url(output: dict) -> tuple[str, str]:
    """
    Extrae la URL del output de fal.ai y determina el tipo (image/video).
    fal.ai puede devolver output.image_url, output.images[0].url, output.video_url, etc.
    """
    if not output:
        return "", "unknown"

    # Video
    if url := output.get("video_url"):
        return url, "video"
    if video := output.get("video"):
        if isinstance(video, dict):
            return video.get("url", ""), "video"

    # Imagen
    if url := output.get("image_url"):
        return url, "image"
    if images := output.get("images"):
        if isinstance(images, list) and images:
            first = images[0]
            if isinstance(first, dict):
                return first.get("url", ""), "image"
            return str(first), "image"

    return "", "unknown"


# ── Endpoint ─────────────────────────────────────────────────

@router.post("/fal", status_code=200)
async def fal_webhook(
    request: Request,
    x_fal_signature: Optional[str] = Header(None),
):
    """
    Payload esperado de fal.ai:
    {
        "request_id": "req_abc123",
        "status": "OK" | "ERROR",
        "output": {
            "image_url": "https://..." | "images": [...] | "video_url": "https://..."
        },
        "error": "mensaje de error"   # solo en ERROR
    }
    """
    # ── Verificar secret ──────────────────────────────────────
    secret = getattr(settings, "FAL_WEBHOOK_SECRET", "")
    if secret and x_fal_signature != secret:
        logger.warning("fal.ai webhook: firma inválida desde %s", request.client.host)
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload: dict = await request.json()
    request_id: str = payload.get("request_id", "")
    status_val: str = payload.get("status", "")
    output: dict = payload.get("output") or {}
    error_msg: str = payload.get("error", "Error desconocido")

    if not request_id:
        return {"ok": True, "skipped": "no request_id"}

    asset_url, asset_type = _extract_output_url(output)

    # ── Actualizar DB ─────────────────────────────────────────
    chat_id: Optional[str] = None

    async with AsyncSessionLocal() as db:
        if status_val == "OK" and asset_url:
            # Guardar asset y descontar tokens
            await db.execute(
                text("""
                    UPDATE assets
                    SET status    = 'ready',
                        url       = :url,
                        type      = :type,
                        updated_at = NOW()
                    WHERE request_id = :rid
                """),
                {"url": asset_url, "type": asset_type, "rid": request_id},
            )

            # Descontar tokens del usuario dueño del asset
            await db.execute(
                text("""
                    UPDATE users u
                    SET tokens_balance = GREATEST(0, tokens_balance - a.tokens_cost)
                    FROM assets a
                    WHERE a.request_id = :rid
                    AND u.id = a.user_id
                """),
                {"rid": request_id},
            )
            logger.info("Asset listo: %s [%s] → %s", request_id, asset_type, asset_url)

        else:
            await db.execute(
                text("""
                    UPDATE assets
                    SET status        = 'failed',
                        error_message = :err,
                        updated_at    = NOW()
                    WHERE request_id = :rid
                """),
                {"err": error_msg, "rid": request_id},
            )
            logger.error("Asset fallido: %s — %s", request_id, error_msg)

        # Obtener chat_id del usuario
        result = await db.execute(
            text("""
                SELECT u.telegram_chat_id
                FROM assets a
                JOIN users u ON u.id = a.user_id
                WHERE a.request_id = :rid
                LIMIT 1
            """),
            {"rid": request_id},
        )
        row = result.fetchone()
        if row:
            chat_id = row.telegram_chat_id

        await db.commit()

    # ── Notificar usuario ─────────────────────────────────────
    if chat_id:
        if status_val == "OK" and asset_url:
            emoji = "🖼️" if asset_type == "image" else "🎬"
            msg = (
                f"{emoji} <b>Tu {asset_type} está lista</b>\n\n"
                f"<a href='{asset_url}'>Ver resultado</a>\n\n"
                "Disponible en tu panel de contenido."
            )
        else:
            msg = (
                "❌ <b>Error al generar tu contenido</b>\n\n"
                f"ID: <code>{request_id}</code>\n"
                "Tus tokens no fueron descontados. Intenta de nuevo."
            )
        await _telegram_notify(chat_id, msg)

    return {"ok": True, "request_id": request_id, "status": status_val}
