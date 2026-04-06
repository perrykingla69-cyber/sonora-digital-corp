"""
Payments — MercadoPago Checkout API
Compra de paquetes de tokens con OXXO, tarjeta y transferencia.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal, get_tenant_session
from app.core.deps import AuthUser

router = APIRouter()
logger = logging.getLogger(__name__)

MP_API = "https://api.mercadopago.com"


# ── Helpers ───────────────────────────────────────────────────

async def _get_package(package_id: str) -> dict:
    async with AsyncSessionLocal() as db:
        r = await db.execute(
            text("SELECT id, name, tokens, price_mxn FROM token_packages WHERE id = :id AND is_active = true"),
            {"id": package_id},
        )
        row = r.fetchone()
    if not row:
        raise HTTPException(404, "Paquete no encontrado")
    return dict(row._mapping)


async def _credit_tokens(user_id: str, tenant_id: str, tokens: int, payment_id: str) -> int:
    """Acredita tokens al usuario. Idempotente por payment_id."""
    async with get_tenant_session(tenant_id) as db:
        # Idempotencia: verificar si ya se procesó este pago
        dup = await db.execute(
            text("SELECT id FROM payments WHERE external_id = :pid LIMIT 1"),
            {"pid": payment_id},
        )
        if dup.fetchone():
            r = await db.execute(
                text("SELECT tokens_balance FROM users WHERE id = :uid"),
                {"uid": user_id},
            )
            return r.scalar_one()

        await db.execute(
            text("UPDATE users SET tokens_balance = tokens_balance + :tok WHERE id = :uid"),
            {"tok": tokens, "uid": user_id},
        )
        await db.execute(
            text("""
                INSERT INTO payments (user_id, tenant_id, external_id, tokens_credited, status)
                VALUES (:uid, :tid, :pid, :tok, 'approved')
            """),
            {"uid": user_id, "tid": tenant_id, "pid": payment_id, "tok": tokens},
        )
        await db.commit()
        r = await db.execute(
            text("SELECT tokens_balance FROM users WHERE id = :uid"),
            {"uid": user_id},
        )
        return r.scalar_one()


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


# ── Schemas ───────────────────────────────────────────────────

class CreatePaymentRequest(BaseModel):
    package_id: str


# ── Endpoints ─────────────────────────────────────────────────

@router.post("/create")
async def create_payment(body: CreatePaymentRequest, current_user: AuthUser, request: Request):
    """
    Crea preferencia de pago en MercadoPago.
    Devuelve init_point para redirigir al usuario al checkout.
    """
    if not getattr(settings, "MP_ACCESS_TOKEN", ""):
        raise HTTPException(503, "Pagos no configurados aún. Contacta al administrador.")

    pkg = await _get_package(body.package_id)
    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    # Obtener email y chat_id del usuario para metadata
    async with get_tenant_session(tid) as db:
        r = await db.execute(
            text("SELECT email, telegram_chat_id, slug FROM users WHERE id = :uid"),
            {"uid": uid},
        )
        user = r.fetchone()

    back_url = f"https://sonoradigitalcorp.com/user/{user.slug}" if user else "https://sonoradigitalcorp.com"

    preference_data = {
        "items": [{
            "id": str(pkg["id"]),
            "title": f"HERMES OS — {pkg['name']}",
            "description": f"{pkg['tokens']:,} tokens para generación de contenido",
            "quantity": 1,
            "currency_id": "MXN",
            "unit_price": float(pkg["price_mxn"]),
        }],
        "payer": {"email": user.email if user else "cliente@hermes.mx"},
        "back_urls": {
            "success": f"{back_url}?payment=success",
            "failure": f"{back_url}?payment=failed",
            "pending": f"{back_url}?payment=pending",
        },
        "auto_return": "approved",
        "notification_url": "https://sonoradigitalcorp.com/webhooks/mercadopago",
        "external_reference": f"{uid}|{tid}|{pkg['id']}|{pkg['tokens']}",
        "metadata": {
            "user_id": uid,
            "tenant_id": tid,
            "package_id": str(pkg["id"]),
            "tokens": pkg["tokens"],
            "chat_id": user.telegram_chat_id if user else "",
        },
        "payment_methods": {
            "excluded_payment_types": [],
            "installments": 1,
        },
    }

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            f"{MP_API}/checkout/preferences",
            headers={
                "Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
            json=preference_data,
        )
        if r.status_code not in (200, 201):
            logger.error("MercadoPago error: %s — %s", r.status_code, r.text)
            raise HTTPException(502, "Error al crear el pago. Intenta de nuevo.")
        data = r.json()

    return {
        "preference_id": data["id"],
        "init_point": data["init_point"],          # producción
        "sandbox_init_point": data.get("sandbox_init_point", ""),  # testing
        "package": {
            "name": pkg["name"],
            "tokens": pkg["tokens"],
            "price_mxn": float(pkg["price_mxn"]),
        },
    }


# ── Webhook MercadoPago ───────────────────────────────────────

@router.post("/webhook/mercadopago", status_code=200)
async def mp_webhook(request: Request):
    """
    Recibe notificaciones de MercadoPago.
    Acredita tokens cuando el pago es aprobado.
    """
    payload = await request.json()
    topic = payload.get("type") or payload.get("topic", "")
    data_id = payload.get("data", {}).get("id") or payload.get("id", "")

    if topic not in ("payment", "merchant_order") or not data_id:
        return {"ok": True, "skipped": topic}

    mp_token = getattr(settings, "MP_ACCESS_TOKEN", "")
    if not mp_token:
        return {"ok": True, "skipped": "no mp token"}

    # Obtener detalles del pago desde MP
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            f"{MP_API}/v1/payments/{data_id}",
            headers={"Authorization": f"Bearer {mp_token}"},
        )
        if r.status_code != 200:
            logger.warning("MP payment fetch failed: %s", r.status_code)
            return {"ok": True, "skipped": "fetch_failed"}
        payment = r.json()

    status = payment.get("status", "")
    if status != "approved":
        logger.info("MP payment %s status=%s — ignorado", data_id, status)
        return {"ok": True, "skipped": f"status={status}"}

    # Parsear external_reference: uid|tid|pkg_id|tokens
    ref = payment.get("external_reference", "")
    parts = ref.split("|")
    if len(parts) != 4:
        logger.error("MP webhook: external_reference inválido: %s", ref)
        return {"ok": True, "skipped": "bad_ref"}

    user_id, tenant_id, pkg_id, tokens_str = parts
    tokens = int(tokens_str)
    amount = payment.get("transaction_amount", 0)

    # Acreditar tokens (idempotente)
    new_balance = await _credit_tokens(user_id, tenant_id, tokens, str(data_id))

    # Notificar al usuario
    meta = payment.get("metadata") or {}
    chat_id = meta.get("chat_id", "")
    if chat_id:
        await _telegram_notify(
            chat_id,
            f"✅ <b>¡Pago aprobado!</b>\n\n"
            f"💳 ${amount:.0f} MXN\n"
            f"⚡ <b>+{tokens:,} tokens</b> acreditados\n"
            f"💰 Saldo actual: <b>{new_balance:,} tokens</b>\n\n"
            f"Ya puedes generar contenido desde tu panel 🚀"
        )

    logger.info("MP pago %s aprobado — %s tokens → user %s", data_id, tokens, user_id)
    return {"ok": True, "tokens_credited": tokens, "new_balance": new_balance}
