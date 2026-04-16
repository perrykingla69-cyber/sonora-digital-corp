"""
Agent: {{AGENT_NAME}}
Type: chat
Description: {{AGENT_DESCRIPTION}}
Verticales: {{VERTICALES}}
Model: {{MODEL}}
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="{{AGENT_NAME}}", description="{{AGENT_DESCRIPTION}}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AGENT_ID = os.getenv("AGENT_ID", "{{AGENT_ID}}")
TENANT_ID = os.getenv("TENANT_ID", "{{TENANT_ID}}")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "google/gemini-2.0-flash-001"  # Gemini Flash — gratis vía OpenRouter

SYSTEM_PROMPT = """Eres {{AGENT_NAME}}, un asistente virtual especializado en {{VERTICALES}}.

{{AGENT_DESCRIPTION}}

Reglas:
- Responde siempre en español
- Sé profesional pero accesible
- Si no sabes algo con certeza, dilo claramente
- No inventes datos, precios, leyes o fechas
- Cita fuentes cuando uses información específica
"""


class ChatRequest(BaseModel):
    message: str
    user_id: str = ""
    conversation_id: str = ""
    context: list[dict] = []


class ChatResponse(BaseModel):
    reply: str
    agent: str
    agent_id: str
    tokens_used: int = 0


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Agregar contexto previo (últimos 10 mensajes)
    for msg in body.context[-10:]:
        messages.append(msg)

    messages.append({"role": "user", "content": body.message})

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "HTTP-Referer": "https://sonoradigitalcorp.com",
                "X-Title": "{{AGENT_NAME}}",
            },
            json={
                "model": MODEL,
                "messages": messages,
                "max_tokens": 800,
                "temperature": 0.7,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    reply = data["choices"][0]["message"]["content"]
    tokens = data.get("usage", {}).get("total_tokens", 0)

    return ChatResponse(
        reply=reply,
        agent="{{AGENT_NAME}}",
        agent_id=AGENT_ID,
        tokens_used=tokens,
    )


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "{{AGENT_NAME}}", "agent_id": AGENT_ID}
