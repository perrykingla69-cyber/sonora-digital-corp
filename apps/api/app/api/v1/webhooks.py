"""
Webhooks — Evolution API (WhatsApp) y Telegram
Entrada de mensajes de canales externos → procesados por HERMES
"""

import hashlib
import hmac
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Header
from typing import Optional
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal

router = APIRouter()


async def _resolve_tenant_by_instance(instance_name: str):
    """Encuentra el tenant dueño de esta instancia de WhatsApp."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("""
                SELECT t.id as tenant_id
                FROM channels c
                JOIN tenants t ON t.id = c.tenant_id
                WHERE c.type = 'whatsapp'
                AND c.config->>'instance_name' = :instance
                AND c.is_active = true
                AND t.is_active = true
            """),
            {"instance": instance_name},
        )
        return result.fetchone()


async def _process_whatsapp_message(payload: dict):
    """Procesa mensaje de WhatsApp y llama a HERMES."""
    from app.agents.hermes import HermesAgent
    from app.core.database import get_tenant_session

    instance = payload.get("instance", "")
    data = payload.get("data", {})
    event = payload.get("event", "")

    if event != "messages.upsert":
        return

    message_data = data.get("message", {})
    remote_jid = data.get("key", {}).get("remoteJid", "")
    from_me = data.get("key", {}).get("fromMe", False)

    if from_me:
        return  # No procesar mensajes propios

    text_content = (
        message_data.get("conversation")
        or message_data.get("extendedTextMessage", {}).get("text")
        or ""
    )
    if not text_content:
        return

    tenant_row = await _resolve_tenant_by_instance(instance)
    if not tenant_row:
        return

    from uuid import UUID
    tenant_id = UUID(str(tenant_row.tenant_id))

    async with get_tenant_session(tenant_id) as db:
        agent = HermesAgent(tenant_id=tenant_id, db=db)
        result = await agent.chat(
            message=text_content,
            conversation_id=None,
            user_id=tenant_id,  # sistema
            channel="whatsapp",
        )

        # Responder via Evolution API
        import httpx
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.EVOLUTION_URL}/message/sendText/{instance}",
                headers={"apikey": settings.EVOLUTION_API_KEY},
                json={
                    "number": remote_jid,
                    "text": result["response"],
                },
            )


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    apikey: Optional[str] = Header(None),
):
    """
    Webhook de Evolution API — valida apikey y procesa en background.
    Fix: Evolution API v2.2.3 bug #1858 — idempotency key para evitar webhook loops.
    """
    if apikey != settings.EVOLUTION_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    payload = await request.json()

    # Idempotency: deduplicar mensajes duplicados (bug Evolution v2.2.3)
    from app.core.redis import redis_client
    msg_key = payload.get("data", {}).get("key", {}).get("id", "")
    event = payload.get("event", "")
    if msg_key:
        dedup_key = f"wa:dedup:{msg_key}:{event}"
        if await redis_client.get(dedup_key):
            return {"status": "duplicate", "skipped": True}
        await redis_client.setex(dedup_key, 30, "1")

    background_tasks.add_task(_process_whatsapp_message, payload)
    return {"status": "queued"}


@router.post("/telegram/{bot_token}")
async def telegram_webhook(
    bot_token: str,
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Webhook de Telegram — el token identifica el canal/tenant."""
    # Validar que el token corresponde a un canal registrado
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("""
                SELECT t.id as tenant_id, c.id as channel_id
                FROM channels c
                JOIN tenants t ON t.id = c.tenant_id
                WHERE c.type = 'telegram'
                AND c.config->>'bot_token_hash' = :hash
                AND c.is_active = true
            """),
            {"hash": hashlib.sha256(bot_token.encode()).hexdigest()},
        )
        channel = result.fetchone()

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    update = await request.json()
    background_tasks.add_task(_process_telegram_update, update, str(channel.tenant_id))
    return {"ok": True}


async def _process_telegram_update(update: dict, tenant_id_str: str):
    from app.agents.hermes import HermesAgent
    from app.core.database import get_tenant_session
    from uuid import UUID

    message = update.get("message", {})
    text_content = message.get("text", "")
    if not text_content or text_content.startswith("/"):
        return

    tenant_id = UUID(tenant_id_str)
    async with get_tenant_session(tenant_id) as db:
        agent = HermesAgent(tenant_id=tenant_id, db=db)
        await agent.chat(
            message=text_content,
            conversation_id=None,
            user_id=tenant_id,
            channel="telegram",
        )
