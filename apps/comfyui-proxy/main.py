"""
ComfyUI Proxy — API wrapper para generación de imágenes/video para ABE Music
Conecta con ComfyUI local (port 8188) o remoto
Workflows: thumbnail_artist, cover_album, social_post, video_thumbnail
"""
import os
import json
import uuid
import httpx
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any

app = FastAPI(title="ComfyUI Proxy — ABE Music Visual", version="1.0.0")

COMFYUI_URL = os.getenv("COMFYUI_URL", "http://localhost:8188")
DREAMINA_API_KEY = os.getenv("DREAMINA_API_KEY", "")


# ── Modelos ────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    workflow: str  # "thumbnail_artist" | "cover_album" | "social_post" | "promo_video"
    prompt: str
    negative_prompt: str = "blurry, low quality, text watermark, ugly"
    artist_name: Optional[str] = None
    style: str = "norteño vaquero moderno"
    width: int = 1024
    height: int = 1024
    steps: int = 20
    seed: int = -1


class GenerateResponse(BaseModel):
    job_id: str
    status: str
    image_url: Optional[str] = None
    message: str


# ── Workflows predefinidos ─────────────────────────────────────

WORKFLOW_PROMPTS = {
    "thumbnail_artist": "professional music artist photo, {artist_name}, norteño regional mexicano style, {prompt}, cinematic lighting, 4K, high detail",
    "cover_album": "album cover art, {artist_name}, {prompt}, norteño mexican music, professional photography, dramatic lighting",
    "social_post": "social media post, {artist_name}, {prompt}, instagram ready, vibrant colors, eye-catching",
    "promo_video": "music video still frame, {artist_name}, {prompt}, cinematic, professional, norteño aesthetic",
}


async def _generate_via_comfyui(request: GenerateRequest) -> dict:
    """Submit to ComfyUI API if available."""
    prompt_text = WORKFLOW_PROMPTS.get(request.workflow, "{prompt}").format(
        artist_name=request.artist_name or "artista",
        prompt=request.prompt,
    )
    # ComfyUI workflow payload (simplified SDXL-turbo compatible)
    workflow = {
        "3": {
            "inputs": {
                "seed": request.seed if request.seed >= 0 else uuid.uuid4().int % (2**32),
                "steps": request.steps,
                "cfg": 7.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
            "class_type": "KSampler",
        },
        "4": {"inputs": {"ckpt_name": "sd_xl_turbo_1.0_fp16.safetensors"}, "class_type": "CheckpointLoaderSimple"},
        "5": {"inputs": {"width": request.width, "height": request.height, "batch_size": 1}, "class_type": "EmptyLatentImage"},
        "6": {"inputs": {"text": prompt_text, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
        "7": {"inputs": {"text": request.negative_prompt, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
        "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
        "9": {"inputs": {"filename_prefix": f"abe_music_{request.workflow}", "images": ["8", 0]}, "class_type": "SaveImage"},
    }

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow})
        r.raise_for_status()
        return r.json()


async def _generate_via_dreamina(request: GenerateRequest) -> dict:
    """Use Dreamina Seedance 2.0 API for video generation."""
    if not DREAMINA_API_KEY:
        return {"status": "mock", "message": "DREAMINA_API_KEY not configured"}

    prompt_text = WORKFLOW_PROMPTS.get(request.workflow, "{prompt}").format(
        artist_name=request.artist_name or "artista",
        prompt=request.prompt,
    )
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.capcut.com/v1/dreamina/generate",
            headers={"Authorization": f"Bearer {DREAMINA_API_KEY}", "Content-Type": "application/json"},
            json={
                "prompt": prompt_text,
                "negative_prompt": request.negative_prompt,
                "width": request.width,
                "height": request.height,
                "duration": 5 if "video" in request.workflow else 0,
                "style": request.style,
            },
        )
        return r.json()


@app.post("/generate", response_model=GenerateResponse)
async def generate_visual(request: GenerateRequest):
    job_id = str(uuid.uuid4())

    # Try ComfyUI first, then Dreamina, then mock
    try:
        result = await _generate_via_comfyui(request)
        return GenerateResponse(
            job_id=job_id,
            status="queued",
            message=f"Enviado a ComfyUI — prompt_id: {result.get('prompt_id', 'unknown')}",
        )
    except Exception:
        pass

    try:
        result = await _generate_via_dreamina(request)
        return GenerateResponse(
            job_id=job_id,
            status="queued",
            message=f"Dreamina task: {result.get('task_id', 'queued')}",
        )
    except Exception:
        pass

    # Mock fallback
    return GenerateResponse(
        job_id=job_id,
        status="mock",
        image_url=f"https://placehold.co/{request.width}x{request.height}/1a1a2e/gold?text={request.artist_name or 'ABE+Music'}",
        message=f"Mock — instala ComfyUI en :{8188} o configura DREAMINA_API_KEY para generación real",
    )


@app.get("/workflows")
async def list_workflows():
    return {"workflows": list(WORKFLOW_PROMPTS.keys()), "comfyui_url": COMFYUI_URL}


@app.get("/health")
async def health():
    comfyui_ok = False
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{COMFYUI_URL}/system_stats")
            comfyui_ok = r.status_code == 200
    except Exception:
        pass
    return {
        "status": "ok",
        "service": "comfyui-proxy",
        "comfyui_connected": comfyui_ok,
        "dreamina_configured": bool(DREAMINA_API_KEY),
    }
