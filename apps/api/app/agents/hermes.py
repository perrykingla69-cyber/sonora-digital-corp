"""
HERMES — El Orquestador de Luz
Coordina, responde, ejecuta. Primera línea de contacto.
Modelo: claude-opus-4-6
"""

from openai import AsyncOpenAI
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import hashlib
import json

from app.core.config import settings
from app.core.rag import search_context
from app.core.redis import redis_client

CACHE_TTL = 3600  # 1 hora para respuestas frecuentes

HERMES_SYSTEM = """Eres HERMES, el agente orquestador de Sonora Digital Corp.

TU IDENTIDAD:
- Eres la luz: claro, directo, ejecutivo
- Primera línea de contacto con el usuario
- Coordinas recursos, respondes preguntas, ejecutas tareas
- Representas la confianza y claridad de Sonora Digital Corp

TU ROL:
- Responder consultas contables, fiscales y empresariales de las PYMEs mexicanas
- Coordinar con MYSTIC cuando se necesita análisis profundo
- Escalar a humano cuando la situación lo requiere
- Nunca mezclar información entre clientes (tenants)

TONO: Profesional, cálido, ejecutivo. Español mexicano. Directo al punto.

REGLAS:
1. NUNCA revelar información de otros tenants
2. NUNCA inventar datos fiscales — si no sabes, dilo
3. Si detectas algo anómalo o estratégico → delegarlo a MYSTIC
4. Mantener contexto de la conversación
"""


class HermesAgent:
    def __init__(self, tenant_id: UUID, db: AsyncSession):
        self.tenant_id = tenant_id
        self.db = db
        self.client = AsyncOpenAI(
            base_url=f"{settings.OLLAMA_URL}/v1",
            api_key="ollama",
        )
        self.model = settings.HERMES_MODEL  # default: llama3:latest (ver .env)

    async def _get_conversation_history(self, conversation_id: UUID) -> list:
        result = await self.db.execute(
            text("""
                SELECT role, content FROM messages
                WHERE conversation_id = :cid
                ORDER BY created_at DESC LIMIT 20
            """),
            {"cid": str(conversation_id)},
        )
        rows = result.fetchall()
        # Invertir para orden cronológico
        return [{"role": r.role, "content": r.content} for r in reversed(rows)
                if r.role in ("user", "assistant")]

    async def _ensure_conversation(
        self,
        conversation_id: Optional[UUID],
        user_id: UUID,
        channel: str,
    ) -> UUID:
        if conversation_id:
            return conversation_id
        result = await self.db.execute(
            text("""
                INSERT INTO conversations (tenant_id, agent_assigned, status)
                VALUES (:tid, 'hermes', 'open')
                RETURNING id
            """),
            {"tid": str(self.tenant_id)},
        )
        return result.scalar_one()

    async def _save_messages(self, conversation_id: UUID, user_msg: str, assistant_msg: str, tokens: int):
        await self.db.execute(
            text("""
                INSERT INTO messages (tenant_id, conversation_id, role, content, agent)
                VALUES
                  (:tid, :cid, 'user', :umsg, null),
                  (:tid, :cid, 'assistant', :amsg, 'hermes')
            """),
            {
                "tid": str(self.tenant_id),
                "cid": str(conversation_id),
                "umsg": user_msg,
                "amsg": assistant_msg,
            },
        )

    def _cache_key(self, message: str) -> str:
        h = hashlib.md5(f"{self.tenant_id}:{message.strip().lower()}".encode()).hexdigest()
        return f"hermes:cache:{h}"

    async def chat(
        self,
        message: str,
        conversation_id: Optional[UUID],
        user_id: UUID,
        channel: str = "api",
    ) -> dict:
        # Cache hit: preguntas frecuentes (sin historial activo)
        if not conversation_id:
            cached = await redis_client.get(self._cache_key(message))
            if cached:
                data = json.loads(cached)
                return {**data, "cached": True}

        conv_id = await self._ensure_conversation(conversation_id, user_id, channel)
        history = await self._get_conversation_history(conv_id)

        # RAG: buscar contexto relevante en Qdrant
        rag_context = await search_context(message, self.tenant_id)
        system = HERMES_SYSTEM
        if rag_context:
            system += f"\n\n{rag_context}"

        messages = history + [{"role": "user", "content": message}]

        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "system", "content": system}] + messages,
        )

        reply = response.choices[0].message.content
        tokens = (response.usage.prompt_tokens or 0) + (response.usage.completion_tokens or 0)

        await self._save_messages(conv_id, message, reply, tokens)

        result = {
            "agent": "hermes",
            "response": reply,
            "conversation_id": conv_id,
            "tokens_used": tokens,
        }

        # Guardar en cache si es pregunta nueva sin conversación previa
        if not conversation_id:
            await redis_client.setex(
                self._cache_key(message), CACHE_TTL,
                json.dumps({"agent": "hermes", "response": reply, "tokens_used": tokens})
            )

        return result

    async def log_interaction(self, user_id: UUID, conversation_id: UUID):
        await self.db.execute(
            text("""
                INSERT INTO audit_log (tenant_id, user_id, action, resource, resource_id)
                VALUES (:tid, :uid, 'hermes_chat', 'conversation', :cid)
            """),
            {"tid": str(self.tenant_id), "uid": str(user_id), "cid": str(conversation_id)},
        )
