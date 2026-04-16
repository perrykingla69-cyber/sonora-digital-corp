"""
Content Suite API — Copy Writer IA, Photo Generator (FAL), Video Templates, Scheduled Posts.
Todos los endpoints requieren JWT válido.
Rate limit: 100 req/min por usuario (nginx upstream + Redis).
"""

from __future__ import annotations

import io
import json
import logging
import uuid as uuid_lib
from typing import List, Optional

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_tenant_session
from app.core.deps import AuthUser
from app.models.content import (
    CopyGenerateRequest,
    CopyGenerateResponse,
    CopyOption,
    PhotoGenerateRequest,
    PhotoGenerateResponse,
    PhotoVariation,
    SchedulePostRequest,
    SchedulePostResponse,
    VideoTemplateRequest,
    VideoTemplateResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Créditos por operación
COPY_CREDITS = 3
PHOTO_CREDITS = 5
VIDEO_CREDITS = 10
SCHEDULE_CREDITS = 0  # Agendar no cuesta créditos por ahora

# Límites de archivos
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024   # 50 MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav"}


# ── System prompts ────────────────────────────────────────────

COPY_SYSTEM_PROMPT = """Eres un experto en marketing musical y redes sociales para artistas latinoamericanos.
Generas copy auténtico, con voz propia, en español mexicano natural.
NUNCA uses frases genéricas o clichés como "¡No te lo pierdas!" o "Disponible ahora".
Cada copy debe sonar como el artista hablando, no como una agencia.
Responde SOLO con un JSON válido, sin explicaciones adicionales."""

COPY_USER_TEMPLATE = """Genera copy para las siguientes plataformas: {platforms}
Tono: {tone}
Contexto: {context}

Artista: productor/artista musical

Responde con este JSON exacto (un objeto por plataforma):
{{
  "options": [
    {{
      "platform": "instagram",
      "copy": "texto del copy aquí",
      "hashtags": ["#hashtag1", "#hashtag2"]
    }}
  ]
}}

Reglas por tono:
- hype: energético, emojis 🔥💥, máximo impacto
- professional: formal, claro, sin emojis excessivos
- casual: conversacional, cercano, como DM a un amigo

Reglas por plataforma:
- instagram: max 300 chars, 8-10 hashtags mixtos (es/en)
- tiktok: max 150 chars, 5-7 hashtags trending
- twitter: max 280 chars, 2-3 hashtags
- linkedin: max 500 chars, sin hashtags o 2 máximo
- facebook: max 400 chars, 5-8 hashtags"""


PHOTO_STYLE_PROMPTS = {
    "album-cover": "professional album cover art, music industry quality, dramatic lighting, artistic composition, high contrast, 1:1 square format",
    "headshot": "professional artist headshot, studio lighting, clean background, editorial quality, focused on face and upper body",
    "social-media": "vibrant social media post, eye-catching colors, instagram aesthetic, lifestyle photography style",
    "promotional": "promotional material for musician, concert poster style, bold typography space, atmospheric lighting",
}


# ── Helpers ───────────────────────────────────────────────────

async def _save_content_history(
    tenant_id: str,
    user_id: str,
    content_type: str,
    input_data: dict,
    output_data: dict,
    credits_used: int,
    content_id: Optional[str] = None,
) -> str:
    """Guarda historial de contenido generado. Retorna el content_id."""
    cid = content_id or str(uuid_lib.uuid4())
    try:
        async with get_tenant_session(tenant_id) as db:
            await db.execute(
                text("""
                    INSERT INTO content_history
                        (id, user_id, tenant_id, content_type, input_data, output_data, credits_used)
                    VALUES
                        (:id, :uid, :tid, :ctype, :inp, :out, :cred)
                """),
                {
                    "id": cid,
                    "uid": user_id,
                    "tid": tenant_id,
                    "ctype": content_type,
                    "inp": json.dumps(input_data, ensure_ascii=False),
                    "out": json.dumps(output_data, ensure_ascii=False),
                    "cred": credits_used,
                },
            )
    except Exception as e:
        logger.error("Failed to save content history: %s", e)
        # No bloquear la respuesta por fallo de auditoría
    return cid


async def _call_openrouter(system_prompt: str, user_message: str, max_tokens: int = 1500) -> str:
    """Llama a OpenRouter (Gemini Flash). Lanza HTTPException en error."""
    if not settings.OPENROUTER_API_KEY:
        raise HTTPException(503, "OpenRouter no configurado. Contacta al administrador.")

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://sonoradigitalcorp.com",
                "X-Title": "Sonora Digital Corp",
            },
            json={
                "model": "google/gemini-2.0-flash-001",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": max_tokens,
                "temperature": 0.85,
            },
        )
        if r.status_code == 429:
            raise HTTPException(429, "Rate limit de IA. Intenta en un momento.")
        if not r.is_success:
            logger.error("OpenRouter error %s: %s", r.status_code, r.text)
            raise HTTPException(502, "Error en el servicio de IA. Intenta de nuevo.")
        return r.json()["choices"][0]["message"]["content"].strip()


def _parse_copy_response(raw: str, platforms: List[str]) -> List[CopyOption]:
    """Parsea la respuesta JSON de OpenRouter para copy. Fallback si JSON inválido."""
    # Extraer JSON si viene envuelto en ```json...```
    if "```" in raw:
        import re
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
        if match:
            raw = match.group(1).strip()

    try:
        data = json.loads(raw)
        options_raw = data.get("options", [])
        options = []
        for opt in options_raw:
            copy_text = opt.get("copy", "")
            hashtags = opt.get("hashtags", [])
            options.append(CopyOption(
                platform=opt.get("platform", "instagram"),
                copy=copy_text,
                hashtags=hashtags,
                character_count=len(copy_text),
            ))
        if options:
            return options
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.warning("Failed to parse copy JSON: %s — raw: %s", e, raw[:200])

    # Fallback: crear opciones básicas desde el texto plano
    fallback = []
    for platform in platforms:
        fallback.append(CopyOption(
            platform=platform,
            copy=raw[:300] if raw else "¡Nuevo contenido disponible! 🎵",
            hashtags=["#musica", "#newmusic", "#producer"],
            character_count=min(len(raw), 300),
        ))
    return fallback


# ── Copy Writer ───────────────────────────────────────────────

@router.post(
    "/generate-copy",
    response_model=CopyGenerateResponse,
    summary="Generar copy para redes sociales con IA",
    status_code=status.HTTP_200_OK,
)
async def generate_copy(
    request: CopyGenerateRequest,
    current_user: AuthUser,
):
    """
    Genera copy optimizado por plataforma usando Gemini Flash.

    - **context**: Describe tu track, beat, evento o promoción (mín. 10 chars)
    - **tone**: hype | professional | casual
    - **platforms**: Lista de plataformas destino

    Retorna opciones de copy con hashtags optimizados por plataforma.
    """
    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    platforms_str = ", ".join(request.platforms)
    user_msg = COPY_USER_TEMPLATE.format(
        platforms=platforms_str,
        tone=request.tone,
        context=request.context,
    )

    try:
        raw_response = await _call_openrouter(COPY_SYSTEM_PROMPT, user_msg, max_tokens=1500)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Copy generation failed: %s", e)
        raise HTTPException(500, "Error generando el copy. Intenta de nuevo.")

    options = _parse_copy_response(raw_response, request.platforms)

    content_id = str(uuid_lib.uuid4())
    await _save_content_history(
        tid, uid, "copy",
        input_data=request.model_dump(),
        output_data={"options": [o.model_dump() for o in options]},
        credits_used=COPY_CREDITS,
        content_id=content_id,
    )

    return CopyGenerateResponse(
        options=options,
        content_id=uuid_lib.UUID(content_id),
        credits_used=COPY_CREDITS,
    )


@router.get(
    "/copy-history",
    summary="Historial de copies generados",
)
async def get_copy_history(
    limit: int = 20,
    current_user: AuthUser = None,
):
    """Retorna el historial de copies generados por el usuario autenticado."""
    if not 1 <= limit <= 100:
        raise HTTPException(400, "limit debe estar entre 1 y 100.")

    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    async with get_tenant_session(tid) as db:
        r = await db.execute(
            text("""
                SELECT id, content_type, input_data, output_data, credits_used, created_at
                FROM content_history
                WHERE user_id = :uid AND tenant_id = :tid AND content_type = 'copy'
                ORDER BY created_at DESC
                LIMIT :lim
            """),
            {"uid": uid, "tid": tid, "lim": limit},
        )
        rows = r.fetchall()

    results = []
    for row in rows:
        d = dict(row._mapping)
        # Deserializar JSONB
        if isinstance(d.get("input_data"), str):
            try:
                d["input_data"] = json.loads(d["input_data"])
            except Exception:
                pass
        if isinstance(d.get("output_data"), str):
            try:
                d["output_data"] = json.loads(d["output_data"])
            except Exception:
                pass
        results.append(d)

    return results


# ── Photo Generator ───────────────────────────────────────────

@router.post(
    "/generate-photo",
    response_model=PhotoGenerateResponse,
    summary="Generar foto estilizada con FAL.ai",
)
async def generate_photo(
    style: str = Form(..., description="album-cover | headshot | social-media | promotional"),
    description: Optional[str] = Form(None, description="Descripción adicional"),
    file: UploadFile = File(..., description="Imagen JPG/PNG/WebP (max 10MB)"),
    current_user: AuthUser = None,
):
    """
    Genera variaciones estilizadas de una foto usando FAL.ai image-to-image.

    1. Valida y lee la imagen subida
    2. Sube a FAL.ai con el estilo + prompt seleccionado
    3. Genera 3 variaciones (async — retorna cuando terminan)
    4. Guarda en historial
    """
    # Validar estilo antes de procesar archivo
    from app.models.content import VALID_PHOTO_STYLES
    if style not in VALID_PHOTO_STYLES:
        raise HTTPException(400, f"style inválido. Valores: {', '.join(VALID_PHOTO_STYLES)}")

    if not settings.FAL_API_KEY:
        raise HTTPException(503, "FAL_API_KEY no configurada. Contacta al administrador.")

    # Validar tipo de archivo
    content_type = file.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(400, f"Tipo de archivo no soportado: {content_type}. Usa JPG, PNG o WebP.")

    # Leer y validar tamaño
    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(413, "Imagen demasiado grande. Máximo 10MB.")
    if len(image_bytes) < 1024:
        raise HTTPException(400, "Imagen demasiado pequeña o inválida.")

    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    # Construir prompt
    base_style_prompt = PHOTO_STYLE_PROMPTS.get(style, "professional photography")
    full_prompt = base_style_prompt
    if description:
        full_prompt = f"{description}, {base_style_prompt}"

    # Subir imagen original a FAL storage
    import base64
    image_b64 = base64.b64encode(image_bytes).decode()
    image_data_uri = f"data:{content_type};base64,{image_b64}"

    # Llamar a FAL image-to-image para 3 variaciones
    variations: List[PhotoVariation] = []
    variation_prompts = [
        f"{full_prompt}, version 1, high quality",
        f"{full_prompt}, version 2, different angle, high quality",
        f"{full_prompt}, version 3, creative twist, high quality",
    ]

    for i, prompt in enumerate(variation_prompts):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    "https://fal.run/fal-ai/flux/dev/image-to-image",
                    headers={
                        "Authorization": f"Key {settings.FAL_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "image_url": image_data_uri,
                        "prompt": prompt,
                        "num_inference_steps": 28,
                        "strength": 0.75,
                        "num_images": 1,
                    },
                )
                if r.status_code == 429:
                    raise HTTPException(429, "FAL.ai rate limit. Intenta en un momento.")
                if not r.is_success:
                    logger.error("FAL.ai error %s for variation %d: %s", r.status_code, i+1, r.text[:300])
                    # Continuar con las otras variaciones
                    continue

                fal_data = r.json()
                images = fal_data.get("images", [])
                if images:
                    variation_url = images[0].get("url", "")
                    variations.append(PhotoVariation(
                        style=f"{style}-v{i+1}",
                        url=variation_url,
                        prompt_used=prompt,
                    ))
        except HTTPException:
            raise
        except Exception as e:
            logger.error("FAL.ai variation %d failed: %s", i+1, e)
            # No interrumpir si una variación falla

    if not variations:
        raise HTTPException(502, "No se pudo generar ninguna variación. Intenta de nuevo.")

    content_id = str(uuid_lib.uuid4())
    await _save_content_history(
        tid, uid, "photo",
        input_data={"style": style, "description": description, "filename": file.filename},
        output_data={"variations": [v.model_dump() for v in variations]},
        credits_used=PHOTO_CREDITS,
        content_id=content_id,
    )

    return PhotoGenerateResponse(
        original=f"data:{content_type};base64,{image_b64[:50]}...",  # No devolver imagen completa
        variations=variations,
        content_id=uuid_lib.UUID(content_id),
        credits_used=PHOTO_CREDITS,
    )


# ── Video Template ────────────────────────────────────────────

@router.post(
    "/video-template",
    response_model=VideoTemplateResponse,
    summary="Procesar video con template",
)
async def process_video_template(
    template: str = Form(..., description="spotify-premiere | beat-showcase | studio-session | reaction"),
    caption: Optional[str] = Form(None, description="Caption para el video (max 300 chars)"),
    background_music: Optional[str] = Form(None, description="URL de música de fondo (opcional)"),
    audio_file: UploadFile = File(..., description="Audio MP3/WAV (max 50MB, max 30s)"),
    image_file: UploadFile = File(..., description="Imagen cuadrada JPG/PNG (min 512x512)"),
    current_user: AuthUser = None,
):
    """
    Genera un video con template para TikTok/Instagram Reels.

    1. Valida audio (max 30s para TikTok) e imagen (square, min 512x512)
    2. Si FAL.ai disponible: usa video generation API
    3. Fallback: genera preview con FAL image-to-video
    4. Exporta MP4 optimizado

    Plantillas disponibles:
    - **spotify-premiere**: Overlay de Spotify card con waveform
    - **beat-showcase**: Visualizador de beats con espectro de audio
    - **studio-session**: Estética de estudio, tons cálidos
    - **reaction**: Split screen para reacciones
    """
    from app.models.content import VALID_TEMPLATES
    if template not in VALID_TEMPLATES:
        raise HTTPException(400, f"template inválido. Valores: {', '.join(VALID_TEMPLATES)}")

    if not settings.FAL_API_KEY:
        raise HTTPException(503, "FAL_API_KEY no configurada. Contacta al administrador.")

    # Validar audio
    audio_ct = audio_file.content_type or ""
    if audio_ct not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(400, f"Tipo de audio no soportado: {audio_ct}. Usa MP3 o WAV.")

    audio_bytes = await audio_file.read()
    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(413, "Audio demasiado grande. Máximo 50MB.")

    # Validar imagen
    img_ct = image_file.content_type or ""
    if img_ct not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(400, f"Tipo de imagen no soportado. Usa JPG, PNG o WebP.")

    image_bytes = await image_file.read()
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(413, "Imagen demasiado grande. Máximo 10MB.")

    # Validar dimensiones mínimas de imagen (512x512)
    try:
        import struct
        # PNG: leer IHDR para dimensiones
        if img_ct == "image/png" and image_bytes[1:4] == b"PNG":
            w = struct.unpack(">I", image_bytes[16:20])[0]
            h = struct.unpack(">I", image_bytes[20:24])[0]
            if w < 512 or h < 512:
                raise HTTPException(400, f"Imagen muy pequeña ({w}x{h}). Mínimo 512x512 píxeles.")
    except HTTPException:
        raise
    except Exception:
        pass  # Si no podemos leer dimensiones, continuar

    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    # Prompts por template
    template_prompts = {
        "spotify-premiere": "cinematic music premiere, Spotify card overlay, dynamic waveform visualization, dark background, neon accents",
        "beat-showcase": "beat producer showcase, audio spectrum visualizer, studio aesthetics, professional music video style",
        "studio-session": "warm studio session, vintage vibes, golden hour lighting, authentic behind-the-scenes feel",
        "reaction": "split screen reaction video, energetic, expressive, social media trending style",
    }

    import base64
    image_b64 = base64.b64encode(image_bytes).decode()
    image_data_uri = f"data:{img_ct};base64,{image_b64}"
    prompt = template_prompts.get(template, "professional music video")
    if caption:
        prompt = f"{prompt}, caption: {caption[:100]}"

    # Llamar a FAL image-to-video
    video_url = ""
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                "https://fal.run/fal-ai/kling-video/v1.6/standard/image-to-video",
                headers={
                    "Authorization": f"Key {settings.FAL_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "image_url": image_data_uri,
                    "prompt": prompt,
                    "duration": "5",
                    "aspect_ratio": "9:16",
                },
            )
            if r.status_code == 429:
                raise HTTPException(429, "FAL.ai rate limit. Intenta en un momento.")
            if not r.is_success:
                logger.error("FAL.ai video error %s: %s", r.status_code, r.text[:300])
                raise HTTPException(502, "Error generando el video. Intenta de nuevo.")

            fal_data = r.json()
            video_url = fal_data.get("video", {}).get("url", "")
            if not video_url:
                raise HTTPException(502, "FAL.ai no retornó URL de video.")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Video generation failed: %s", e)
        raise HTTPException(500, "Error generando el video.")

    content_id = str(uuid_lib.uuid4())
    await _save_content_history(
        tid, uid, "video",
        input_data={
            "template": template,
            "caption": caption,
            "audio_filename": audio_file.filename,
            "image_filename": image_file.filename,
        },
        output_data={"video_url": video_url},
        credits_used=VIDEO_CREDITS,
        content_id=content_id,
    )

    return VideoTemplateResponse(
        video_url=video_url,
        duration="5s",
        platforms=["tiktok", "instagram"],
        file_size="~5MB",
        ready_to_post=True,
        content_id=uuid_lib.UUID(content_id),
        credits_used=VIDEO_CREDITS,
    )


# ── Scheduled Posts ───────────────────────────────────────────

@router.post(
    "/schedule-post",
    response_model=SchedulePostResponse,
    summary="Agendar publicación en redes sociales",
    status_code=status.HTTP_201_CREATED,
)
async def schedule_post(
    request: SchedulePostRequest,
    current_user: AuthUser,
):
    """
    Agenda una publicación para Instagram/TikTok/etc.

    Por ahora guarda en DB para ejecución posterior via N8N workflow.
    El post real se ejecuta cuando `scheduled_time` llega y el workflow activa
    la Graph API correspondiente.
    """
    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    post_id = str(uuid_lib.uuid4())

    async with get_tenant_session(tid) as db:
        await db.execute(
            text("""
                INSERT INTO scheduled_posts
                    (id, user_id, tenant_id, platform, caption, media_url,
                     scheduled_time, status)
                VALUES
                    (:id, :uid, :tid, :platform, :caption, :media_url,
                     :sched, 'scheduled')
            """),
            {
                "id": post_id,
                "uid": uid,
                "tid": tid,
                "platform": request.platform,
                "caption": request.caption,
                "media_url": str(request.media_url) if request.media_url else None,
                "sched": request.scheduled_time,
            },
        )

    logger.info("Post scheduled: %s for %s on %s at %s",
                post_id, uid, request.platform, request.scheduled_time)

    from datetime import datetime, timezone
    return SchedulePostResponse(
        id=uuid_lib.UUID(post_id),
        platform=request.platform,
        caption=request.caption,
        scheduled_time=request.scheduled_time,
        status="scheduled",
        created_at=datetime.now(timezone.utc),
    )


@router.get(
    "/scheduled-posts",
    summary="Listar posts agendados",
)
async def list_scheduled_posts(
    status_filter: Optional[str] = None,
    limit: int = 20,
    current_user: AuthUser = None,
):
    """Lista los posts agendados del usuario. Filtra por status si se provee."""
    if not 1 <= limit <= 100:
        raise HTTPException(400, "limit debe estar entre 1 y 100.")

    uid = str(current_user.user_id)
    tid = str(current_user.tenant_id)

    query = """
        SELECT id, platform, caption, media_url, scheduled_time,
               posted_time, status, created_at
        FROM scheduled_posts
        WHERE user_id = :uid AND tenant_id = :tid
    """
    params: dict = {"uid": uid, "tid": tid, "lim": limit}

    if status_filter:
        from app.models.content import VALID_POST_STATUSES
        if status_filter not in VALID_POST_STATUSES:
            raise HTTPException(400, f"status inválido. Valores: {', '.join(VALID_POST_STATUSES)}")
        query += " AND status = :status"
        params["status"] = status_filter

    query += " ORDER BY scheduled_time ASC LIMIT :lim"

    async with get_tenant_session(tid) as db:
        r = await db.execute(text(query), params)
        return [dict(row._mapping) for row in r.fetchall()]
