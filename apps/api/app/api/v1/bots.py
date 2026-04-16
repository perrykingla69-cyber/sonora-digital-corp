"""
Bot Factory endpoints — crear bots Telegram/WhatsApp, health check.
"""

import httpx
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import text
import os

from app.core.database import get_tenant_session
from app.core.security import encrypt
from app.core.deps import AuthUser

logger = logging.getLogger(__name__)
router = APIRouter()

CLAWBOT_URL = os.getenv("CLAWBOT_URL", "http://clawbot:3003")


# ── Schemas ───────────────────────────────────────────────────

class CreateBotRequest(BaseModel):
    agent_id: str
    channel: str = "telegram"  # telegram | whatsapp | discord
    config: dict = {}


class BotResponse(BaseModel):
    bot_id: str
    channel: str
    status: str
    webhook_url: str
    instructions: str


class BotHealthResponse(BaseModel):
    id: str
    status: str
    last_check: Optional[str]
    uptime: str
    messages_processed_today: int


# ── Endpoints ─────────────────────────────────────────────────

@router.post("/create", response_model=BotResponse, status_code=201)
async def create_bot(
    body: CreateBotRequest,
    background_tasks: BackgroundTasks,
    current_user: AuthUser,
):
    """
    Crea un bot para un agente existente.
    Genera webhook URL y registra en DB.
    """
    valid_channels = {"telegram", "whatsapp", "discord"}
    if body.channel not in valid_channels:
        raise HTTPException(400, f"Canal inválido. Válidos: {valid_channels}")

    async with get_tenant_session(current_user.tenant_id) as db:
        # Verificar que el agente pertenece al usuario
        a = await db.execute(
            text("""
                SELECT id, status FROM agent_deployments
                WHERE id = :aid AND user_id = :uid
            """),
            {"aid": body.agent_id, "uid": str(current_user.user_id)},
        )
        agent = a.fetchone()
        if not agent:
            raise HTTPException(404, "Agente no encontrado")
        if agent.status not in ("active", "creating"):
            raise HTTPException(
                400,
                f"El agente está en estado '{agent.status}'. "
                "Solo se puede crear un bot si el agente está activo."
            )

        # Crear bot en DB
        webhook_url = (
            f"https://sonoradigitalcorp.com/webhook/{body.channel}/{body.agent_id}"
        )
        r = await db.execute(
            text("""
                INSERT INTO bots
                    (agent_deployment_id, user_id, tenant_id, channel, webhook_url, status)
                VALUES
                    (:aid, :uid, current_tenant_id(), :channel, :webhook, 'created')
                RETURNING id
            """),
            {
                "aid": body.agent_id,
                "uid": str(current_user.user_id),
                "channel": body.channel,
                "webhook": webhook_url,
            },
        )
        bot_id = r.scalar_one()

    # Registrar en ClawBot en background
    background_tasks.add_task(
        _register_with_clawbot,
        str(bot_id),
        body.agent_id,
        str(current_user.tenant_id),
        body.channel,
        webhook_url,
        body.config,
    )

    instructions = _get_instructions(body.channel, webhook_url, str(bot_id))

    return BotResponse(
        bot_id=str(bot_id),
        channel=body.channel,
        status="created",
        webhook_url=webhook_url,
        instructions=instructions,
    )


@router.get("/{bot_id}/health", response_model=BotHealthResponse)
async def get_bot_health(bot_id: str, current_user: AuthUser):
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("""
                SELECT id, status, health_check_last, uptime_pct, messages_today
                FROM bots
                WHERE id = :bid AND user_id = :uid
            """),
            {"bid": bot_id, "uid": str(current_user.user_id)},
        )
        bot = r.fetchone()
    if not bot:
        raise HTTPException(404, "Bot no encontrado")

    return BotHealthResponse(
        id=str(bot.id),
        status=bot.status,
        last_check=bot.health_check_last.isoformat() if bot.health_check_last else None,
        uptime=f"{float(bot.uptime_pct):.1f}%",
        messages_processed_today=bot.messages_today or 0,
    )


@router.get("/")
async def list_bots(current_user: AuthUser):
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("""
                SELECT
                    b.id, b.name, b.channel, b.status,
                    b.webhook_url, b.health_check_last, b.messages_today,
                    b.uptime_pct, b.created_at,
                    ad.name AS agent_name
                FROM bots b
                LEFT JOIN agent_deployments ad ON ad.id = b.agent_deployment_id
                WHERE b.user_id = :uid
                ORDER BY b.created_at DESC
            """),
            {"uid": str(current_user.user_id)},
        )
    return [
        {k: str(v) if hasattr(v, 'hex') else
         v.isoformat() if hasattr(v, 'isoformat') else
         float(v) if hasattr(v, 'is_integer') else v
         for k, v in dict(row._mapping).items()}
        for row in r.fetchall()
    ]


@router.delete("/{bot_id}")
async def delete_bot(bot_id: str, current_user: AuthUser):
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("""
                UPDATE bots SET status = 'destroying', updated_at = NOW()
                WHERE id = :bid AND user_id = :uid
                RETURNING id
            """),
            {"bid": bot_id, "uid": str(current_user.user_id)},
        )
        if not r.fetchone():
            raise HTTPException(404, "Bot no encontrado")
    return {"detail": "Bot marcado para eliminación"}


# ── Internal ──────────────────────────────────────────────────

def _get_instructions(channel: str, webhook_url: str, bot_id: str) -> str:
    if channel == "telegram":
        return (
            f"Para activar tu bot Telegram:\n"
            f"1. Habla con @BotFather en Telegram\n"
            f"2. Crea un nuevo bot con /newbot\n"
            f"3. Copia el token y ejecuta:\n"
            f"   POST /api/v1/bots/{bot_id}/set-token {{token: 'TU_TOKEN'}}\n"
            f"Tu webhook URL: {webhook_url}"
        )
    elif channel == "whatsapp":
        return (
            f"Para activar tu bot WhatsApp:\n"
            f"1. Ve a Evolution API en tu dashboard\n"
            f"2. Crea una instancia y escanea el QR\n"
            f"3. Configura el webhook: {webhook_url}"
        )
    return f"Webhook URL configurado: {webhook_url}"


async def _register_with_clawbot(
    bot_id: str,
    agent_id: str,
    tenant_id: str,
    channel: str,
    webhook_url: str,
    config: dict,
):
    """Registra el bot en ClawBot para manejo de mensajes."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{CLAWBOT_URL}/api/v1/bots/register",
                json={
                    "bot_id": bot_id,
                    "agent_id": agent_id,
                    "tenant_id": tenant_id,
                    "channel": channel,
                    "webhook_url": webhook_url,
                    "config": config,
                },
            )
            resp.raise_for_status()
            logger.info(f"Bot {bot_id} registrado en ClawBot")
    except Exception as e:
        logger.error(f"Error registrando bot {bot_id} en ClawBot: {e}")
