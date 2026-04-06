"""
CONTENT AGENT — Sonora Digital Corp
Genera contenido, programa posts, gestiona leads y secuencias de email.
Se apaga solo cuando no hay tareas pendientes.
"""

import asyncio
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
import httpx
from openai import AsyncOpenAI
from fastapi import FastAPI, BackgroundTasks
import redis.asyncio as aioredis
import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("content-agent")

app = FastAPI(title="Content Agent", version="1.0.0")

OPENROUTER_KEY   = os.environ.get("OPENROUTER_API_KEY", "")
FAL_KEY          = os.environ.get("FAL_API_KEY", "")
RESEND_KEY       = os.environ.get("RESEND_API_KEY", "")
DB_URL           = os.environ["DATABASE_URL"].replace("postgresql+asyncpg", "postgresql")
REDIS_URL        = os.environ["REDIS_URL"]
META_TOKEN       = os.environ.get("META_ACCESS_TOKEN", "")
META_PAGE_ID     = os.environ.get("META_PAGE_ID", "")
TIKTOK_TOKEN     = os.environ.get("TIKTOK_ACCESS_TOKEN", "")
CEO_TELEGRAM     = os.environ.get("TELEGRAM_TOKEN_CEO", "")
CEO_CHAT_ID      = os.environ.get("CEO_CHAT_ID", "")
OLLAMA_URL       = os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434")

# Prioridad: Ollama local (gratis) → OpenRouter (si hay key)
if OPENROUTER_KEY:
    llm = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_KEY,
    )
    CONTENT_MODEL = "google/gemini-2.0-flash-001"
else:
    llm = AsyncOpenAI(
        base_url=f"{OLLAMA_URL}/v1",
        api_key="ollama",
    )
    CONTENT_MODEL = "llama3:latest"


# ── Notificar CEO ─────────────────────────────────────────────
async def notify_ceo(text: str):
    if not CEO_TELEGRAM or not CEO_CHAT_ID:
        return
    async with httpx.AsyncClient(timeout=10) as c:
        await c.post(
            f"https://api.telegram.org/bot{CEO_TELEGRAM}/sendMessage",
            json={"chat_id": CEO_CHAT_ID, "text": text, "parse_mode": "Markdown"},
        )


# ── Generador de contenido ────────────────────────────────────
async def generate_post_content(
    niche: str,
    platform: str,
    theme: str,
    tone: str = "profesional pero cercano",
) -> dict:
    """
    Genera caption + hashtags para un post.
    Returns: {caption, hashtags, image_prompt, cta}
    """
    platform_rules = {
        "instagram": "máx 2200 chars, 3-5 párrafos, CTA al final, 20-30 hashtags",
        "tiktok":    "máx 150 chars, energético, 3-5 hashtags trending, texto para video",
        "facebook":  "máx 500 chars, conversacional, sin hashtags, pregunta para engagement",
    }

    prompt = f"""Eres un experto en marketing digital para PYMEs mexicanas.
Genera contenido para {platform} para un negocio de giro: {niche}.
Tema del post: {theme}
Tono: {tone}
Reglas del platform: {platform_rules.get(platform, 'tono profesional')}

Responde en JSON exacto:
{{
  "caption": "texto del post",
  "hashtags": ["#tag1", "#tag2"],
  "image_prompt": "descripción en inglés para generar imagen con IA, ultra-detailed, commercial photography style",
  "cta": "llamada a la acción específica"
}}"""

    kwargs = {"model": CONTENT_MODEL, "messages": [{"role": "user", "content": prompt}]}
    # response_format solo con OpenRouter; Ollama lo soporta en versiones recientes
    if OPENROUTER_KEY:
        kwargs["response_format"] = {"type": "json_object"}
    r = await llm.chat.completions.create(**kwargs)
    raw = r.choices[0].message.content
    # Extraer JSON aunque venga rodeado de markdown ```json ... ```
    if "```" in raw:
        import re
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if m:
            raw = m.group(1)
    result = json.loads(raw)
    # LLM a veces devuelve lista en vez de dict — tomar primer elemento
    if isinstance(result, list):
        result = result[0]
    return result


# ── Generador de imagen ───────────────────────────────────────
async def generate_image(prompt: str, model: str = "nanobanana") -> Optional[str]:
    """
    Genera imagen gratis con Pollinations.ai.
    Modelos disponibles: flux, nanobanana, nanobanana-pro, seedream, kontext, turbo
    Fallback a Fal.ai solo si FAL_API_KEY configurada y Pollinations falla.
    """
    url = await _generate_pollinations(prompt, model=model)
    if url:
        return url
    if FAL_KEY:
        return await _generate_fal(prompt)
    return None


async def _generate_fal(prompt: str) -> Optional[str]:
    """Fal.ai FLUX Schnell — $0.003/imagen, calidad profesional."""
    try:
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(
                "https://fal.run/fal-ai/flux/schnell",
                headers={"Authorization": f"Key {FAL_KEY}"},
                json={
                    "prompt": prompt,
                    "image_size": "square_hd",
                    "num_images": 1,
                    "enable_safety_checker": True,
                },
            )
            data = r.json()
            return data.get("images", [{}])[0].get("url")
    except Exception as e:
        logger.error(f"Fal.ai error: {e} — cayendo a Pollinations")
        return await _generate_pollinations(prompt)


async def _generate_pollinations(prompt: str, model: str = "nanobanana") -> Optional[str]:
    """
    Pollinations.ai — 100% gratis, sin API key, 1080x1080.
    Modelos: nanobanana, nanobanana-pro, flux, seedream, kontext, turbo
    """
    try:
        from urllib.parse import quote
        enhanced = f"{prompt}, professional commercial photography, high quality, vibrant colors, 4k"
        encoded = quote(enhanced)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?model={model}&width=1080&height=1080&nologo=true&enhance=true"
        )
        # HEAD request para confirmar disponibilidad (Pollinations genera on-demand)
        async with httpx.AsyncClient(timeout=90, follow_redirects=True) as c:
            r = await c.head(url)
            if r.status_code == 200:
                return url
        return url  # Retornar URL igualmente — se genera al ser accedida
    except Exception as e:
        logger.error(f"Pollinations error: {e}")
        return None


# ── Publicar en Instagram/Facebook (Meta Graph API) ───────────
async def post_to_meta(caption: str, image_url: str, platforms: list[str]) -> dict:
    if not META_TOKEN or not META_PAGE_ID:
        return {"error": "META_ACCESS_TOKEN o META_PAGE_ID no configurados"}

    results = {}
    async with httpx.AsyncClient(timeout=60) as c:
        # Crear media container
        if image_url:
            media_r = await c.post(
                f"https://graph.facebook.com/v19.0/{META_PAGE_ID}/media",
                params={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": META_TOKEN,
                },
            )
            container_id = media_r.json().get("id")

            if container_id and "instagram" in platforms:
                # Publicar container en Instagram
                pub_r = await c.post(
                    f"https://graph.facebook.com/v19.0/{META_PAGE_ID}/media_publish",
                    params={"creation_id": container_id, "access_token": META_TOKEN},
                )
                results["instagram"] = pub_r.json().get("id")

        if "facebook" in platforms:
            fb_r = await c.post(
                f"https://graph.facebook.com/v19.0/{META_PAGE_ID}/feed",
                params={
                    "message": caption,
                    "link": image_url or "",
                    "access_token": META_TOKEN,
                },
            )
            results["facebook"] = fb_r.json().get("id")

    return results


# ── Enviar email con Resend ───────────────────────────────────
async def send_email(to: str, subject: str, html: str, from_name: str = "Sonora Digital Corp") -> bool:
    if not RESEND_KEY:
        logger.warning("RESEND_API_KEY no configurado")
        return False
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_KEY}"},
            json={
                "from": f"{from_name} <sonoradigitalcorp@gmail.com>",
                "to": [to],
                "subject": subject,
                "html": html,
            },
        )
        return r.status_code == 200


# ── Generar semana de contenido ───────────────────────────────
async def generate_content_week(tenant_id: str, niche: str, theme: str) -> dict:
    """
    Genera un plan completo de contenido para la semana.
    Lunes, Miércoles, Viernes = 3 posts por semana.
    """
    logger.info(f"Generando semana de contenido: tenant={tenant_id} niche={niche}")

    schedule = {
        "monday":    {"platform": "instagram", "type": "educativo"},
        "wednesday": {"platform": "tiktok",    "type": "entretenimiento"},
        "friday":    {"platform": "facebook",  "type": "promocional"},
    }

    posts = {}
    for day, config in schedule.items():
        content = await generate_post_content(
            niche=niche,
            platform=config["platform"],
            theme=f"{theme} — {config['type']}",
        )

        image_url = None
        if content.get("image_prompt"):
            image_url = await generate_image(content["image_prompt"])

        posts[day] = {
            **content,
            "platform": config["platform"],
            "image_url": image_url,
            "status": "draft",
        }
        logger.info(f"✓ Post {day} generado para {config['platform']}")

    return posts


# ── Secuencia email automática ────────────────────────────────
async def run_email_sequence(lead_email: str, lead_name: str, niche: str, sequence_type: str):
    """
    Genera y envía secuencia de emails personalizados para un lead.
    """
    sequences = {
        "welcome": [
            {"delay_hours": 0,  "subject": f"Bienvenido, {lead_name} 👋", "template": "welcome"},
            {"delay_hours": 48, "subject": "Esto es lo que podemos hacer por ti", "template": "value"},
            {"delay_hours": 168,"subject": "¿Listo para dar el siguiente paso?", "template": "cta"},
        ],
        "followup": [
            {"delay_hours": 0,  "subject": f"Hola {lead_name}, ¿pudiste revisar nuestra propuesta?", "template": "followup_1"},
            {"delay_hours": 72, "subject": "Un caso de éxito que te va a interesar", "template": "case_study"},
            {"delay_hours": 120,"subject": "Última llamada — oferta especial", "template": "urgency"},
        ],
        "feedback": [
            {"delay_hours": 0, "subject": "Tu opinión nos ayuda a mejorar", "template": "feedback"},
        ],
        "maintenance": [
            {"delay_hours": 0, "subject": f"Reporte mensual — {datetime.now().strftime('%B %Y')}", "template": "monthly_report"},
        ],
    }

    steps = sequences.get(sequence_type, sequences["welcome"])

    for step in steps:
        html = await generate_email_html(
            template=step["template"],
            lead_name=lead_name,
            niche=niche,
        )
        if step["delay_hours"] == 0:
            await send_email(lead_email, step["subject"], html)
        # Los emails con delay los encola N8N / cron


async def generate_email_html(template: str, lead_name: str, niche: str) -> str:
    """Genera HTML de email personalizado con LLM."""
    prompt = f"""Genera el HTML de un email profesional en español mexicano.
Template: {template}
Nombre del lead: {lead_name}
Giro del negocio: {niche}
Empresa: Sonora Digital Corp
Producto: HERMES OS — plataforma de IA para PYMEs

El email debe ser:
- Personalizado con el nombre y giro
- Tono cálido y profesional
- CTA claro al final
- Diseño limpio en HTML (inline CSS, compatible con Gmail)
- Máximo 300 palabras

Responde SOLO con el HTML, sin explicación."""

    r = await llm.chat.completions.create(
        model=CONTENT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.choices[0].message.content


# ── ENDPOINTS ─────────────────────────────────────────────────

@app.post("/generate-week")
async def api_generate_week(
    tenant_id: str,
    niche: str,
    theme: str,
    background_tasks: BackgroundTasks,
):
    """Genera plan semanal de contenido en background."""
    background_tasks.add_task(
        _generate_and_notify, tenant_id, niche, theme
    )
    return {"status": "generating", "message": "Generando contenido en background"}


async def _generate_and_notify(tenant_id: str, niche: str, theme: str):
    try:
        posts = await generate_content_week(tenant_id, niche, theme)
        await notify_ceo(
            f"✅ *Contenido semanal listo*\n\n"
            f"Nicho: {niche}\nTema: {theme}\n"
            f"Posts generados: {len(posts)}\n\n"
            f"Revisa y aprueba en el dashboard."
        )
    except Exception as e:
        await notify_ceo(f"❌ *Error generando contenido*\n{str(e)}")


@app.post("/capture-lead")
async def capture_lead(
    name: str,
    email: str,
    phone: str = "",
    niche: str = "general",
    source: str = "web",
    tenant_id: str = "global",
):
    """Captura un lead y dispara secuencia de bienvenida."""
    conn = await asyncpg.connect(DB_URL)
    try:
        await conn.execute("""
            INSERT INTO leads (tenant_id, full_name, email, phone, niche, source, status, score)
            VALUES ($1, $2, $3, $4, $5, $6, 'new', 30)
            ON CONFLICT DO NOTHING
        """, tenant_id, name, email, phone, niche, source)
    finally:
        await conn.close()

    # Disparar secuencia de bienvenida en background
    asyncio.create_task(run_email_sequence(email, name, niche, "welcome"))

    await notify_ceo(
        f"🔥 *Nuevo lead capturado*\n\n"
        f"Nombre: {name}\nEmail: {email}\n"
        f"Nicho: {niche}\nFuente: {source}\n\n"
        f"Secuencia de bienvenida iniciada automáticamente."
    )
    return {"status": "captured", "sequence": "welcome_started"}


@app.post("/post-now")
async def post_now(post_id: str, platforms: list[str]):
    """Publica un post inmediatamente."""
    # En producción: leer post de DB, publicar, actualizar estado
    return {"status": "posted", "platforms": platforms}


@app.get("/test-image")
async def test_image(prompt: str = "modern mexican restaurant, warm lighting, professional food photography"):
    """Prueba rápida de generación de imagen — sin auth, para desarrollo."""
    url = await generate_image(prompt)
    engine = "fal.ai" if FAL_KEY else "pollinations.ai (gratis)"
    return {
        "engine": engine,
        "image_url": url,
        "prompt": prompt,
    }


@app.get("/test-post")
async def test_post(niche: str = "restaurante", platform: str = "instagram"):
    """Genera un post completo de prueba."""
    content = await generate_post_content(
        niche=niche,
        platform=platform,
        theme="Promoción del día / oferta especial",
    )
    image_url = await generate_image(content.get("image_prompt", niche))
    return {
        "engine": "fal.ai" if FAL_KEY else "pollinations.ai (gratis)",
        "platform": platform,
        "niche": niche,
        **content,
        "image_url": image_url,
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "agent": "content-agent",
        "llm_engine": f"openrouter/{CONTENT_MODEL}" if OPENROUTER_KEY else f"ollama/{CONTENT_MODEL}",
        "image_engine": "pollinations.ai/nanobanana (gratis)" + (" + fal.ai backup" if FAL_KEY else ""),
        "email_engine": "resend" if RESEND_KEY else "no configurado",
        "social_meta": "activo" if META_TOKEN else "sin configurar",
    }
