from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
import asyncio
import json
import hashlib

class ChannelType(Enum):
    WHATSAPP = auto()
    TELEGRAM = auto()
    WEB_CHAT = auto()
    EMAIL = auto()
    SMS = auto()

class MessagePriority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

@dataclass
class ConversationContext:
    tenant_id: str
    user_id: str
    session_id: str
    channel_origin: ChannelType
    current_intent: Optional[str] = None
    entities_extracted: Dict[str, Any] = field(default_factory=dict)
    pending_confirmations: List[str] = field(default_factory=list)
    last_message_at: datetime = field(default_factory=datetime.now)
    conversation_history: List[Dict] = field(default_factory=list)
    cross_channel_sessions: List[str] = field(default_factory=list)

@dataclass
class UnifiedMessage:
    message_id: str
    context: ConversationContext
    content: str
    content_type: str
    priority: MessagePriority
    requires_response: bool
    suggested_actions: List[Dict] = field(default_factory=list)
    internal_metadata: Dict = field(default_factory=dict)

class OmnichannelOrchestrator:
    def __init__(self, qdrant_client=None):
        self.qdrant = qdrant_client
        self.active_contexts: Dict[str, ConversationContext] = {}
        self.channel_handlers: Dict[ChannelType, Callable] = {}
        self.brain_api_url = "http://localhost:8000/api/brain"

    def register_channel_handler(self, channel: ChannelType, handler: Callable):
        self.channel_handlers[channel] = handler

    async def process_incoming_message(self, channel: ChannelType, payload: Dict[str, Any]) -> UnifiedMessage:
        user_id = self._extract_user_id(channel, payload)
        tenant_id = await self._resolve_tenant(user_id, channel)
        session_id = self._get_or_create_session(tenant_id, user_id, channel)
        context = self.active_contexts.get(session_id)
        if not context:
            context = ConversationContext(tenant_id=tenant_id, user_id=user_id, session_id=session_id, channel_origin=channel)
            self.active_contexts[session_id] = context
        await self._enrich_context(context)
        intent, entities = await self._extract_intent(payload.get('text', ''), context)
        context.current_intent = intent
        context.entities_extracted.update(entities)
        message = UnifiedMessage(
            message_id=self._generate_message_id(payload),
            context=context,
            content=payload.get('text', ''),
            content_type=self._detect_content_type(payload),
            priority=self._determine_priority(intent, context),
            requires_response=self._needs_response(intent),
            suggested_actions=await self._generate_suggestions(intent, entities, context)
        )
        if message.requires_response:
            response = await self._consult_brain(message)
            await self._deliver_response(response, context, channel)
        context.conversation_history.append({'role': 'user', 'content': message.content, 'timestamp': datetime.now().isoformat(), 'intent': intent})
        context.last_message_at = datetime.now()
        return message

    async def send_cross_channel_notification(self, tenant_id: str, notification: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL):
        channels = await self._get_user_channels(tenant_id)
        primary_channel = self._select_optimal_channel(channels, priority)
        success = await self._send_to_channel(primary_channel, notification)
        if not success and priority in [MessagePriority.CRITICAL, MessagePriority.HIGH]:
            for fallback in [c for c in channels if c != primary_channel]:
                success = await self._send_to_channel(fallback, notification)
                if success:
                    break
        return success

    def _extract_user_id(self, channel: ChannelType, payload: Dict) -> str:
        extractors = {
            ChannelType.WHATSAPP: lambda p: f"wa_{p.get('from')}",
            ChannelType.TELEGRAM: lambda p: f"tg_{p.get('from', {}).get('id')}",
            ChannelType.WEB_CHAT: lambda p: f"web_{p.get('session_id')}"
        }
        return extractors.get(channel, lambda p: f"unknown_{hashlib.md5(str(p).encode()).hexdigest()[:8]}")(payload)

    async def _resolve_tenant(self, user_id: str, channel: ChannelType) -> str:
        # Implementar: consulta a base de datos para resolver tenant desde user_id
        return "default_tenant"

    def _get_or_create_session(self, tenant_id: str, user_id: str, channel: ChannelType) -> str:
        session_key = f"{tenant_id}:{user_id}:{channel.name}"
        return hashlib.sha256(session_key.encode()).hexdigest()[:16]

    async def _enrich_context(self, context: ConversationContext):
        # Implementar: cargar historial previo desde Qdrant/Redis
        pass

    async def _extract_intent(self, text: str, context: ConversationContext) -> Tuple[str, Dict]:
        import httpx
        prompt = f"""
        Analiza la intención del usuario en contexto fiscal mexicano:
        Mensaje: "{text}"
        Contexto previo: {context.current_intent or 'Ninguno'}
        
        Responde en JSON: {{"intent": "...", "entities": {{...}}, "confidence": 0.0}}
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={"model": "qwen2.5-coder:32b", "prompt": prompt, "format": "json", "stream": False},
                timeout=15.0
            )
        result = json.loads(response.json().get("response", "{}"))
        return result.get("intent", "unknown"), result.get("entities", {})

    def _detect_content_type(self, payload: Dict) -> str:
        if payload.get('document'):
            return "document"
        if payload.get('image'):
            return "image"
        if payload.get('voice'):
            return "voice"
        return "text"

    def _determine_priority(self, intent: str, context: ConversationContext) -> MessagePriority:
        critical_intents = ['vencimiento_urgente', 'error_declaracion', 'auditoria_notificacion']
        high_intents = ['consulta_mve', 'cfdi_problema', 'saldo_favor']
        if intent in critical_intents:
            return MessagePriority.CRITICAL
        if intent in high_intents:
            return MessagePriority.HIGH
        return MessagePriority.NORMAL

    def _needs_response(self, intent: str) -> bool:
        return intent not in ['saludo', 'despedida', 'feedback_positivo']

    async def _generate_suggestions(self, intent: str, entities: Dict, context: ConversationContext) -> List[Dict]:
        suggestions = []
        if intent == 'consulta_mve':
            suggestions.append({"text": "Generar MVE", "action": "generate_mve", "params": entities})
            suggestions.append({"text": "Validar documentos", "action": "validate_docs", "params": {}})
        elif intent == 'consulta_iva':
            suggestions.append({"text": "Ver estado de IVA", "action": "check_iva_status", "params": {}})
            suggestions.append({"text": "Generar declaración", "action": "generate_iva_return", "params": {}})
        return suggestions

    async def _consult_brain(self, message: UnifiedMessage) -> Dict:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.brain_api_url}/ask",
                json={
                    "question": message.content,
                    "context": {
                        "tenant_id": message.context.tenant_id,
                        "history": message.context.conversation_history[-5:],
                        "entities": message.context.entities_extracted
                    }
                },
                timeout=30.0
            )
        return response.json()

    async def _deliver_response(self, response: Dict, context: ConversationContext, channel: ChannelType):
        handler = self.channel_handlers.get(channel)
        if handler:
            await handler({
                "user_id": context.user_id,
                "content": response.get("answer", "Lo siento, no pude procesar tu consulta."),
                "actions": response.get("suggested_actions", [])
            })

    def _generate_message_id(self, payload: Dict) -> str:
        return hashlib.sha256(f"{payload}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]

    async def _get_user_channels(self, tenant_id: str) -> List[ChannelType]:
        # Implementar: consulta a base de datos de preferencias de usuario
        return [ChannelType.WHATSAPP, ChannelType.TELEGRAM, ChannelType.WEB_CHAT]

    def _select_optimal_channel(self, channels: List[ChannelType], priority: MessagePriority) -> ChannelType:
        priority_map = {
            MessagePriority.CRITICAL: [ChannelType.WHATSAPP, ChannelType.SMS, ChannelType.TELEGRAM],
            MessagePriority.HIGH: [ChannelType.TELEGRAM, ChannelType.WHATSAPP, ChannelType.EMAIL],
            MessagePriority.NORMAL: [ChannelType.WEB_CHAT, ChannelType.EMAIL],
            MessagePriority.LOW: [ChannelType.EMAIL, ChannelType.WEB_CHAT]
        }
        preferred = priority_map.get(priority, channels)
        for p in preferred:
            if p in channels:
                return p
        return channels[0] if channels else ChannelType.EMAIL

    async def _send_to_channel(self, channel: ChannelType, notification: Dict) -> bool:
        handler = self.channel_handlers.get(channel)
        if not handler:
            return False
        try:
            await handler(notification)
            return True
        except Exception:
            return False

    async def sync_context_across_channels(self, session_id: str):
        """Sincroniza contexto de conversación entre todos los canales del usuario"""
        context = self.active_contexts.get(session_id)
        if not context:
            return
        for channel in context.cross_channel_sessions:
            if channel != context.channel_origin:
                await self._notify_context_update(channel, context)
