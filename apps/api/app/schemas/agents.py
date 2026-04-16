"""
Pydantic schemas para endpoints de HERMES y MYSTIC.
Validación automática de requests y responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class HermesChatRequest(BaseModel):
    """Request para POST /api/v1/agents/hermes/chat"""
    tenant_id: UUID = Field(..., description="UUID del tenant")
    message: str = Field(..., min_length=1, max_length=5000, description="Pregunta o mensaje del usuario")
    context: Optional[str] = Field(None, max_length=10000, description="Contexto adicional (opcional)")
    use_rag: bool = Field(True, description="Usar búsqueda RAG en Qdrant")


class HermesChatResponse(BaseModel):
    """Response para POST /api/v1/agents/hermes/chat"""
    response: str = Field(..., description="Respuesta de HERMES")
    sources: List[str] = Field(default_factory=list, description="Fuentes RAG utilizadas")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Score de confianza (0.0-1.0)")
    processing_time_ms: int = Field(..., description="Tiempo procesamiento en ms")
    used_mock: bool = Field(False, description="True si usó fallback mock (OpenRouter no respondió)")


class MysticAnalyzeRequest(BaseModel):
    """Request para GET /api/v1/agents/mystic/analyze"""
    tenant_id: UUID = Field(..., description="UUID del tenant")
    analysis_type: str = Field(..., regex=r"^(fiscal|food|business)$", description="Tipo de análisis")
    data: Optional[str] = Field(None, max_length=10000, description="Texto a analizar (para POST)")


class AlertItem(BaseModel):
    """Estructura de alerta"""
    level: str = Field(..., regex=r"^(critical|warning|info)$", description="Nivel de severidad")
    message: str = Field(..., description="Mensaje de alerta")
    code: Optional[str] = Field(None, description="Código de error/alerta")


class MysticAnalyzeResponse(BaseModel):
    """Response para GET /api/v1/agents/mystic/analyze"""
    analysis: str = Field(..., description="Análisis profundo MYSTIC")
    alerts: List[AlertItem] = Field(default_factory=list, description="Lista de alertas detectadas")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones accionables")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de generación")
    used_mock: bool = Field(False, description="True si usó fallback mock")
