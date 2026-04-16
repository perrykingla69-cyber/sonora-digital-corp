"""
Agent: {{AGENT_NAME}}
Type: webhook
Description: {{AGENT_DESCRIPTION}}
"""

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import httpx
import os
import json
import hmac
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="{{AGENT_NAME}} — Webhook Agent")

AGENT_ID = os.getenv("AGENT_ID", "{{AGENT_ID}}")
TENANT_ID = os.getenv("TENANT_ID", "{{TENANT_ID}}")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
MODEL = "google/gemini-2.0-flash-001"

WEBHOOK_PROMPT = """Eres {{AGENT_NAME}}, un procesador de webhooks especializado en {{VERTICALES}}.

{{AGENT_DESCRIPTION}}

Cuando recibes un webhook:
1. Analiza el payload
2. Determina qué acción tomar
3. Devuelve una respuesta clara y accionable
4. Si se requiere acción externa, describe exactamente qué hacer"""


class WebhookPayload(BaseModel):
    event: str = ""
    data: dict = {}
    source: str = ""


@app.post("/webhook")
async def receive_webhook(request: Request):
    """Recibe cualquier webhook y lo procesa con IA."""
    body_bytes = await request.body()

    # Verificar firma si hay secret configurado
    if WEBHOOK_SECRET:
        signature = request.headers.get("X-Webhook-Signature", "")
        expected = hmac.new(
            WEBHOOK_SECRET.encode(),
            body_bytes,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(f"sha256={expected}", signature):
            raise HTTPException(401, "Firma inválida")

    try:
        payload = json.loads(body_bytes)
    except json.JSONDecodeError:
        payload = {"raw": body_bytes.decode("utf-8", errors="ignore")}

    # Procesar con IA
    prompt = f"""Webhook recibido:
{json.dumps(payload, indent=2, ensure_ascii=False)}

Analiza este evento y determina:
1. Qué ocurrió exactamente
2. Si requiere acción inmediata
3. Qué respuesta/acción tomar"""

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": WEBHOOK_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 500,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    analysis = data["choices"][0]["message"]["content"]
    logger.info(f"Webhook procesado: {analysis[:100]}")

    return {
        "status": "processed",
        "event": payload.get("event", "unknown"),
        "analysis": analysis,
        "agent": "{{AGENT_NAME}}",
    }


@app.post("/webhook/{event_type}")
async def receive_typed_webhook(event_type: str, request: Request):
    """Webhook tipado para eventos específicos."""
    body_bytes = await request.body()
    try:
        payload = json.loads(body_bytes)
    except Exception:
        payload = {}

    logger.info(f"Evento {event_type} recibido: {str(payload)[:200]}")
    return {"status": "received", "event": event_type}


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "{{AGENT_NAME}}", "agent_id": AGENT_ID}
