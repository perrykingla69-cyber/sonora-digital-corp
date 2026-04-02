"""
MYSTIC — La Estratega de Sombra
Analiza lo oculto, detecta patrones, advierte riesgos.
Opera en la oscuridad para proteger desde la luz.
Modelo: claude-sonnet-4-6
"""

from openai import AsyncOpenAI
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings

MYSTIC_SYSTEM = """Eres MYSTIC, el agente estratega de Sonora Digital Corp.

TU IDENTIDAD:
- Eres la sombra: observas, analizas, detectas lo que otros no ven
- Actúas en la luz pero tu fuerza está en ver en la oscuridad
- Eres la inteligencia estratégica detrás de HERMES
- Detectas anomalías, riesgos fiscales, oportunidades ocultas

TU ROL:
- Análisis profundo de situaciones financieras y empresariales
- Detección de riesgos fiscales y contables antes de que escalen
- Inteligencia competitiva y estratégica para el CEO
- Identificar lo que nadie más ve: los patrones, las grietas, los peligros
- Análisis de conversaciones para detectar intenciones y contexto

TONO: Analítico, preciso, estratégico. A veces poético pero siempre útil.
Español mexicano. Hablas directo cuando lo que encontraste importa.

FORMATO DE RESPUESTA:
- OBSERVACIÓN: Qué detectas
- ANÁLISIS: Por qué importa
- RIESGO/OPORTUNIDAD: Nivel (🔴🟡🟢) + descripción
- RECOMENDACIÓN: Acción concreta

REGLAS:
1. NUNCA revelar información de otros tenants
2. Siempre basar el análisis en datos — nunca especular sin evidencia
3. Si el riesgo es crítico → alertar con 🔴 y urgencia
4. Eres el seguro de HERMES, no su reemplazo
"""


class MysticAgent:
    def __init__(self, tenant_id: UUID, db: AsyncSession):
        self.tenant_id = tenant_id
        self.db = db
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.model = settings.MYSTIC_MODEL

    async def _get_tenant_context(self) -> str:
        """Obtiene contexto del tenant para análisis contextualizado."""
        result = await self.db.execute(
            text("SELECT name, plan, settings FROM tenants WHERE id = current_tenant_id()"),
        )
        tenant = result.fetchone()
        if not tenant:
            return ""
        return f"Empresa: {tenant.name} | Plan: {tenant.plan}"

    async def _ensure_conversation(self, conversation_id: Optional[UUID]) -> UUID:
        if conversation_id:
            return conversation_id
        result = await self.db.execute(
            text("""
                INSERT INTO conversations (tenant_id, agent_assigned, status)
                VALUES (:tid, 'mystic', 'open')
                RETURNING id
            """),
            {"tid": str(self.tenant_id)},
        )
        return result.scalar_one()

    async def analyze(
        self,
        message: str,
        conversation_id: Optional[UUID],
        user_id: UUID,
    ) -> dict:
        conv_id = await self._ensure_conversation(conversation_id)
        tenant_ctx = await self._get_tenant_context()

        system = MYSTIC_SYSTEM
        if tenant_ctx:
            system += f"\n\nCONTEXTO DEL CLIENTE:\n{tenant_ctx}"

        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message},
            ],
        )

        reply = response.choices[0].message.content
        tokens = (response.usage.prompt_tokens or 0) + (response.usage.completion_tokens or 0)

        await self.db.execute(
            text("""
                INSERT INTO messages (tenant_id, conversation_id, role, content, agent, tokens_used)
                VALUES
                  (:tid, :cid, 'user', :umsg, null, 0),
                  (:tid, :cid, 'assistant', :amsg, 'mystic', :tokens)
            """),
            {
                "tid": str(self.tenant_id),
                "cid": str(conv_id),
                "umsg": message,
                "amsg": reply,
                "tokens": tokens,
            },
        )

        return {
            "agent": "mystic",
            "response": reply,
            "conversation_id": conv_id,
            "tokens_used": tokens,
        }

    async def shadow_scan(self, tenant_id: UUID) -> dict:
        """
        Scan proactivo: MYSTIC revisa el tenant en busca de anomalías.
        Ejecutado por cron o triggers de N8N.
        """
        result = await self.db.execute(
            text("""
                SELECT
                    COUNT(*) FILTER (WHERE status = 'open') as open_conversations,
                    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '24h') as messages_24h,
                    COUNT(*) FILTER (WHERE status = 'pending') as pending_docs
                FROM conversations c
                LEFT JOIN messages m ON m.conversation_id = c.id
                LEFT JOIN documents d ON d.tenant_id = c.tenant_id
                WHERE c.tenant_id = current_tenant_id()
            """),
        )
        stats = result.fetchone()

        prompt = f"""Análisis de actividad del tenant:
- Conversaciones abiertas: {stats.open_conversations}
- Mensajes últimas 24h: {stats.messages_24h}
- Documentos pendientes: {stats.pending_docs}

¿Hay algo anómalo? ¿Qué requiere atención?"""

        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=512,
            messages=[
                {"role": "system", "content": MYSTIC_SYSTEM},
                {"role": "user", "content": prompt},
            ],
        )

        return {
            "scan": "shadow_scan",
            "analysis": response.choices[0].message.content,
            "stats": dict(stats._mapping),
        }
