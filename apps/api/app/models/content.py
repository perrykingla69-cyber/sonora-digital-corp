"""
Pydantic models para Content Suite API.
Importado por app/api/v1/content_suite.py
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ── Copy Writer ───────────────────────────────────────────────

VALID_TONES = {"hype", "professional", "casual"}
VALID_PLATFORMS = {"instagram", "tiktok", "twitter", "linkedin", "facebook"}


class CopyGenerateRequest(BaseModel):
    """Solicitud de generación de copy para redes sociales."""
    context: str = Field(..., min_length=10, max_length=2000,
                         description="Descripción del track, evento o promoción")
    tone: str = Field(default="hype", description="hype | professional | casual")
    platforms: List[str] = Field(default=["instagram"],
                                 description="Plataformas destino: instagram, tiktok, twitter, linkedin")

    @field_validator("tone")
    @classmethod
    def validate_tone(cls, v: str) -> str:
        if v not in VALID_TONES:
            raise ValueError(f"tone inválido. Valores: {', '.join(VALID_TONES)}")
        return v

    @field_validator("platforms")
    @classmethod
    def validate_platforms(cls, v: List[str]) -> List[str]:
        for p in v:
            if p not in VALID_PLATFORMS:
                raise ValueError(f"platform '{p}' inválida. Valores: {', '.join(VALID_PLATFORMS)}")
        if not v:
            raise ValueError("platforms no puede estar vacío")
        return list(set(v))  # dedup


class CopyOption(BaseModel):
    """Una opción de copy para una plataforma específica."""
    platform: str
    copy: str
    hashtags: List[str]
    character_count: int


class CopyGenerateResponse(BaseModel):
    """Respuesta de generación de copy — lista de opciones por plataforma."""
    options: List[CopyOption]
    content_id: UUID
    credits_used: int


# ── Photo Generator ───────────────────────────────────────────

VALID_PHOTO_STYLES = {"album-cover", "headshot", "social-media", "promotional"}


class PhotoGenerateRequest(BaseModel):
    """Solicitud de generación de foto estilizada."""
    style: str = Field(..., description="album-cover | headshot | social-media | promotional")
    description: Optional[str] = Field(None, max_length=500,
                                       description="Descripción adicional del estilo deseado")

    @field_validator("style")
    @classmethod
    def validate_style(cls, v: str) -> str:
        if v not in VALID_PHOTO_STYLES:
            raise ValueError(f"style inválido. Valores: {', '.join(VALID_PHOTO_STYLES)}")
        return v


class PhotoVariation(BaseModel):
    """Una variación generada de la foto."""
    style: str
    url: str
    prompt_used: str


class PhotoGenerateResponse(BaseModel):
    """Respuesta de generación de foto — original + variaciones."""
    original: str           # URL de la imagen original subida
    variations: List[PhotoVariation]
    content_id: UUID
    credits_used: int


# ── Video Template ────────────────────────────────────────────

VALID_TEMPLATES = {"spotify-premiere", "beat-showcase", "studio-session", "reaction"}


class VideoTemplateRequest(BaseModel):
    """Solicitud de procesamiento de video con template."""
    template: str = Field(..., description="spotify-premiere | beat-showcase | studio-session | reaction")
    caption: Optional[str] = Field(None, max_length=300, description="Caption para el video")
    background_music: Optional[str] = Field(None, max_length=500, description="URL o nombre de música de fondo")

    @field_validator("template")
    @classmethod
    def validate_template(cls, v: str) -> str:
        if v not in VALID_TEMPLATES:
            raise ValueError(f"template inválido. Valores: {', '.join(VALID_TEMPLATES)}")
        return v


class VideoTemplateResponse(BaseModel):
    """Respuesta de procesamiento de video."""
    video_url: str
    duration: str           # e.g. "15s"
    platforms: List[str]    # ["tiktok", "instagram"]
    file_size: str          # e.g. "2.3MB"
    ready_to_post: bool
    content_id: UUID
    credits_used: int


# ── Scheduled Posts ───────────────────────────────────────────

VALID_POST_PLATFORMS = {"instagram", "tiktok", "twitter", "linkedin", "facebook"}
VALID_POST_STATUSES = {"scheduled", "posted", "failed", "cancelled"}


class SchedulePostRequest(BaseModel):
    """Solicitud para agendar un post."""
    content_id: UUID = Field(..., description="ID del contenido generado (copy, foto o video)")
    caption: str = Field(..., min_length=1, max_length=2200, description="Caption del post")
    platform: str = Field(..., description="instagram | tiktok | twitter | linkedin | facebook")
    scheduled_time: datetime = Field(..., description="Hora de publicación en UTC")
    media_url: Optional[str] = Field(None, max_length=2048, description="URL del archivo media a publicar")

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        if v not in VALID_POST_PLATFORMS:
            raise ValueError(f"platform inválida. Valores: {', '.join(VALID_POST_PLATFORMS)}")
        return v

    @field_validator("scheduled_time")
    @classmethod
    def validate_future(cls, v: datetime) -> datetime:
        from datetime import timezone
        now = datetime.now(timezone.utc)
        # Hacer timezone-aware si no lo es
        if v.tzinfo is None:
            from datetime import timezone
            v = v.replace(tzinfo=timezone.utc)
        if v <= now:
            raise ValueError("scheduled_time debe ser una fecha futura")
        return v


class SchedulePostResponse(BaseModel):
    """Respuesta al agendar un post."""
    id: UUID
    platform: str
    caption: str
    scheduled_time: datetime
    status: str
    created_at: datetime
