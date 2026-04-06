"""
Content Generation — fal.ai + OpenRouter
Genera imágenes, videos, captions y hashtags consumiendo tokens del usuario.
"""

from __future__ import annotations

import logging
import uuid as uuid_lib
from typing import Literal, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal, get_tenant_session
from app.core.deps import AuthUser

router = APIRouter()
logger = logging.getLogger(__name__)

# ── Costos por tipo de contenido ─────────────────────────────
CONTENT_COSTS = {
    "instagram_image":  10,
    "facebook_post":     5,
    "video_short":      50,
    "caption":           3,
}

# ── Modelos fal.ai por tipo ───────────────────────────────────
FAL_MODELS = {
    "instagram_image": "fal-ai/flux/schnell",
    "facebook_post":   "fal-ai/flux/schnell",
    "video_short":     "fal-ai/kling-video/v1.6/standard/image-to-video",
}

# ── Prompts de sistema por tipo ───────────────────────────────
CAPTION_SYSTEM_PROMPT = """Eres un experto en marketing digital para PYMEs mexicanas.
Genera contenido atractivo, natural y en español mexicano.
Responde SOLO con el caption y hashtags, sin explicaciones adicionales."""

CAPTION_USER_TEMPLATE = """Genera un caption para {platform} sobre: {topic}

Negocio: {business_type}

Formato de respuesta:
[Caption de 2-3 oraciones, emoji al inicio]

[5-8 hashtags relevantes en español e inglés]"""


# ── Schemas ───────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    content_type: Literal["instagram_image", "facebook_post", "video_short", "caption"]
    topic: str
    business_type: Optional[str] = "general"


class GenerateResponse(BaseModel):
    asset_id: str
    content_type: str
    status: str        # "ready" (caption/texto) | "processing" (imagen/video async)
    result: Optional[str] = None      # Para caption: texto generado
    tokens_spent: int
    tokens_remaining: int


# ── Helpers ───────────────────────────────────────────────────

async def _check_and_deduct_tokens(user_id: str, tenant_id: str, cost: int) -> int:
    """Verifica saldo y descuenta tokens. Devuelve saldo restante."""
    async with get_tenant_session(tenant_id) as db:
        r = await db.execute(
            text("SELECT tokens_balance FROM users WHERE id = :uid FOR UPDATE"),
            {"uid": user_id},
        )
        row = r.fetchone()
        if not row:
            raise HTTPException(404, "Usuario no encontrado")
        balance = row.tokens_balance
        if balance < cost:
            raise HTTPException(
                402,
                f"Tokens insuficientes. Necesitas {cost}, tienes {balance}. "
                "Compra un paquete desde tu panel."
            )
        new_balance = balance - cost
        await db.execute(
            text("UPDATE users SET tokens_balance = :bal WHERE id = :uid"),
            {"bal": new_balance, "uid": user_id},
        )
        await db.commit()
    return new_balance


async def _create_asset_record(
    tenant_id: str, user_id: str, content_type: str,
    tokens_cost: int, request_id: Optional[str] = None,
    status: str = "pending"
) -> str:
    """Crea registro en assets y devuelve el UUID interno."""
    asset_id = str(uuid_lib.uuid4())
    async with get_tenant_session(tenant_id) as db:
        await db.execute(
            text("""
                INSERT INTO assets
                    (id, tenant_id, user_id, request_id, type, status, tokens_cost)
                VALUES
                    (:id, :tid, :uid, :rid, :type, :status, :cost)
            """),
            {
                "id": asset_id,
                "tid": tenant_id,
                "uid": user_id,
                "rid": request_id or asset_id,
                "type": content_type,
                "status": status,
                "cost": tokens_cost,
            },
        )
        await db.commit()
    return asset_id


async def _generate_caption(topic: str, business_type: str, platform: str) -> str:
    """Genera caption con OpenRouter (Gemini Flash). Síncrono y barato."""
    if not settings.OPENROUTER_API_KEY:
        return f"✨ {topic}\n\n#negocio #emprendimiento #mexico"

    user_msg = CAPTION_USER_TEMPLATE.format(
        platform=platform, topic=topic, business_type=business_type
    )
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://sonoradigitalcorp.com",
            },
            json={
                "model": settings.HERMES_MODEL,
                "messages": [
                    {"role": "system", "content": CAPTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                "max_tokens": 300,
                "temperature": 0.8,
            },
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()


async def _submit_fal_job(model: str, prompt: str, content_type: str) -> str:
    """Envía job a fal.ai y devuelve request_id."""
    if not settings.FAL_API_KEY:
        raise HTTPException(503, "FAL_API_KEY no configurada. Contacta al administrador.")

    webhook_url = f"https://sonoradigitalcorp.com/webhooks/fal"

    payload: dict = {}
    if content_type in ("instagram_image", "facebook_post"):
        payload = {
            "prompt": prompt,
            "image_size": "square_hd" if content_type == "instagram_image" else "landscape_16_9",
            "num_inference_steps": 4,
            "num_images": 1,
        }
    elif content_type == "video_short":
        payload = {
            "prompt": prompt,
            "duration": "5",
            "aspect_ratio": "9:16",
        }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"https://queue.fal.run/{model}",
            headers={
                "Authorization": f"Key {settings.FAL_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                **payload,
                "webhook_url": webhook_url,
            },
        )
        r.raise_for_status()
        data = r.json()
        return data.get("request_id", str(uuid_lib.uuid4()))


# ── Endpoint principal ────────────────────────────────────────

@router.post("/generate", response_model=GenerateResponse)
async def generate_content(body: GenerateRequest, current_user: AuthUser):
    """
    Genera contenido usando tokens del usuario.
    - caption: respuesta inmediata vía OpenRouter
    - imagen/video: envío async a fal.ai, webhook actualiza cuando termina
    """
    cost = CONTENT_COSTS.get(body.content_type, 10)
    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    # 1. Verificar y descontar tokens
    remaining = await _check_and_deduct_tokens(uid, tid, cost)

    # 2. Caption/texto — síncrono
    if body.content_type == "caption":
        platform = "Instagram / Facebook"
        try:
            text_result = await _generate_caption(body.topic, body.business_type or "general", platform)
        except Exception as e:
            # Reembolsar tokens si falla
            async with get_tenant_session(tid) as db:
                await db.execute(
                    text("UPDATE users SET tokens_balance = tokens_balance + :cost WHERE id = :uid"),
                    {"cost": cost, "uid": uid},
                )
                await db.commit()
            logger.error("Caption generation failed: %s", e)
            raise HTTPException(500, "Error generando el caption. Tus tokens fueron devueltos.")

        asset_id = await _create_asset_record(tid, uid, "caption", cost, status="ready")

        # Guardar el texto en el asset
        async with get_tenant_session(tid) as db:
            await db.execute(
                text("UPDATE assets SET url = :url WHERE id = :aid"),
                {"url": text_result, "aid": asset_id},
            )
            await db.commit()

        return GenerateResponse(
            asset_id=asset_id,
            content_type=body.content_type,
            status="ready",
            result=text_result,
            tokens_spent=cost,
            tokens_remaining=remaining,
        )

    # 3. Imagen / Video — async vía fal.ai
    fal_model = FAL_MODELS.get(body.content_type)
    if not fal_model:
        raise HTTPException(400, f"Tipo de contenido no soportado: {body.content_type}")

    prompt = f"{body.topic}. Estilo profesional para negocio {body.business_type}. Alta calidad."

    try:
        request_id = await _submit_fal_job(fal_model, prompt, body.content_type)
    except HTTPException:
        raise
    except Exception as e:
        # Reembolsar tokens
        async with get_tenant_session(tid) as db:
            await db.execute(
                text("UPDATE users SET tokens_balance = tokens_balance + :cost WHERE id = :uid"),
                {"cost": cost, "uid": uid},
            )
            await db.commit()
        logger.error("fal.ai submit failed: %s", e)
        raise HTTPException(500, "Error enviando a fal.ai. Tus tokens fueron devueltos.")

    asset_id = await _create_asset_record(
        tid, uid, body.content_type, cost, request_id=request_id
    )

    return GenerateResponse(
        asset_id=asset_id,
        content_type=body.content_type,
        status="processing",
        result=None,
        tokens_spent=cost,
        tokens_remaining=remaining,
    )


@router.get("/assets")
async def list_assets(current_user: AuthUser):
    """Lista los assets del usuario autenticado."""
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("""
                SELECT id, type, status, url, tokens_cost, created_at
                FROM assets
                WHERE user_id = :uid
                ORDER BY created_at DESC
                LIMIT 20
            """),
            {"uid": str(current_user.user_id)},
        )
        return [dict(row._mapping) for row in r.fetchall()]


@router.get("/packages")
async def list_packages():
    """Lista paquetes de tokens disponibles."""
    async with AsyncSessionLocal() as db:
        r = await db.execute(
            text("""
                SELECT id, name, tokens, price_mxn, badge, is_promo
                FROM token_packages
                WHERE is_active = true
                ORDER BY price_mxn
            """)
        )
        return [dict(row._mapping) for row in r.fetchall()]
