"""
MYSTIC Shared Types - Contratos y esquemas compartidos
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


# ── Tenant & User ─────────────────────────────────────────────────────────────

class TenantConfig(BaseModel):
    """Configuración de tenant (cliente/empresa)."""
    id: str
    name: str
    rfc: Optional[str] = None
    plan: Literal["free", "starter", "pro", "enterprise"] = "starter"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    settings: Dict[str, Any] = Field(default_factory=dict)
    qdrant_collection: str = "mystic_knowledge"
    allowed_tools: List[str] = Field(default_factory=lambda: ["rag_query", "n8n_trigger"])
    rate_limits: Dict[str, int] = Field(default_factory=lambda: {"requests_per_minute": 60})


class UserContext(BaseModel):
    """Contexto del usuario en la sesión."""
    user_id: str
    email: str
    tenant_id: str
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    session_id: Optional[str] = None


# ── Brain IA ───────────────────────────────────────────────────────────────────

class BrainRequest(BaseModel):
    """Request para el Brain IA."""
    query: str
    tenant_id: str
    user_context: Optional[UserContext] = None
    conversation_id: Optional[str] = None
    history: List[Dict[str, str]] = Field(default_factory=list)
    tools_enabled: bool = True
    max_tokens: int = 2048
    temperature: float = 0.7


class BrainResponse(BaseModel):
    """Respuesta del Brain IA."""
    answer: str
    sources: List[str] = Field(default_factory=list)
    tool_calls: List["ToolCallResult"] = Field(default_factory=list)
    confidence: float = 0.0
    latency_ms: int = 0
    conversation_id: str
    requires_action: bool = False


class ToolCallResult(BaseModel):
    """Resultado de llamada a herramienta."""
    tool_name: str
    status: Literal["success", "error"]
    result: Any = None
    error: Optional[str] = None


# ── Tools & Skills ─────────────────────────────────────────────────────────────

class ToolDefinition(BaseModel):
    """Definición de herramienta ejecutable."""
    name: str
    description: str
    category: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    requires_auth: bool = True
    allowed_roles: List[str] = Field(default_factory=lambda: ["admin", "contador"])
    rate_limit: Optional[int] = None


class ToolResult(BaseModel):
    """Resultado estandarizado de herramienta."""
    tool_name: str
    status: Literal["success", "error"]
    data: Any = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    tenant_id: Optional[str] = None
    execution_time_ms: Optional[int] = None


class SkillDefinition(BaseModel):
    """Definición de Skill (herramienta + contexto)."""
    id: str
    name: str
    description: str
    tool: ToolDefinition
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)


# ── Workflows ──────────────────────────────────────────────────────────────────

class WorkflowTrigger(BaseModel):
    """Configuración de trigger de workflow."""
    type: Literal["cron", "webhook", "event"]
    cron_expression: Optional[str] = None
    webhook_path: Optional[str] = None
    event_name: Optional[str] = None
    enabled: bool = True
    tenant_filter: List[str] = Field(default_factory=list)


# ── RAG ────────────────────────────────────────────────────────────────────────

class RAGDocument(BaseModel):
    """Documento indexado en Qdrant."""
    id: str
    content: str
    title: str
    topic: str
    tenant_id: str
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedded: bool = False
    embedding_model: str = "nomic-embed-text"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class EmbeddingConfig(BaseModel):
    """Configuración de embeddings."""
    model: str = "nomic-embed-text"
    dimensions: int = 768
    batch_size: int = 10
    collection_name: str = "mystic_knowledge"
    distance: Literal["cosine", "dot", "euclid"] = "cosine"
