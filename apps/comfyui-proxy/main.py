"""
ComfyUI Proxy — API wrapper para generación de imágenes/video para ABE Music
Fallback chain: ComfyUI local (port 8188) → fal.ai (free tier) → placeholder mock
Workflows: thumbnail_artist, cover_album, social_post, promo_video
"""
import os
import uuid
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="ComfyUI Proxy — ABE Music Visual", version="1.2.0")

COMFYUI_URL = os.getenv("COMFYUI_URL", "http://localhost:8188")
FAL_API_KEY = os.getenv("FAL_API_KEY", "")  # opcional: fal.ai free tier como fallback


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


def _build_image_workflow(prompt_text: str, negative: str, width: int, height: int, steps: int, seed: int) -> dict:
    """SDXL-Turbo workflow para imágenes — CPU compatible."""
    return {
        "4": {"inputs": {"ckpt_name": "sd_xl_turbo_1.0_fp16.safetensors"}, "class_type": "CheckpointLoaderSimple"},
        "5": {"inputs": {"width": width, "height": height, "batch_size": 1}, "class_type": "EmptyLatentImage"},
        "6": {"inputs": {"text": prompt_text, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
        "7": {"inputs": {"text": negative, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
        "3": {"inputs": {"seed": seed if seed >= 0 else uuid.uuid4().int % (2**32), "steps": steps, "cfg": 1.0, "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 1.0, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}, "class_type": "KSampler"},
        "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
        "9": {"inputs": {"filename_prefix": "abe_music_img", "images": ["8", 0]}, "class_type": "SaveImage"},
    }


def _build_video_workflow(prompt_text: str, negative: str, steps: int, seed: int) -> dict:
    """AnimateDiff workflow para video corto (16 frames, CPU compatible)."""
    return {
        "1": {"inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"}, "class_type": "CheckpointLoaderSimple"},
        "2": {"inputs": {"model_name": "mm_sd_v15_v2.ckpt", "beta_schedule": "linear", "linear_start": 0.00085, "linear_end": 0.012}, "class_type": "ADE_LoadAnimateDiffModel"},
        "3": {"inputs": {"text": prompt_text, "clip": ["1", 1]}, "class_type": "CLIPTextEncode"},
        "4": {"inputs": {"text": negative, "clip": ["1", 1]}, "class_type": "CLIPTextEncode"},
        "5": {"inputs": {"width": 512, "height": 512, "batch_size": 16}, "class_type": "EmptyLatentImage"},
        "6": {"inputs": {"seed": seed if seed >= 0 else uuid.uuid4().int % (2**32), "steps": steps, "cfg": 7.5, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0, "model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0], "latent_image": ["5", 0]}, "class_type": "KSampler"},
        "7": {"inputs": {"samples": ["6", 0], "vae": ["1", 2]}, "class_type": "VAEDecode"},
        "8": {"inputs": {"filename_prefix": "abe_music_vid", "images": ["7", 0]}, "class_type": "SaveImage"},
    }


async def _generate_via_comfyui(request: GenerateRequest) -> dict:
    """Submit to local ComfyUI (open source, sin costo)."""
    prompt_text = WORKFLOW_PROMPTS.get(request.workflow, "{prompt}").format(
        artist_name=request.artist_name or "artista",
        prompt=request.prompt,
    )
    is_video = request.workflow == "promo_video"
    workflow = (
        _build_video_workflow(prompt_text, request.negative_prompt, request.steps, request.seed)
        if is_video
        else _build_image_workflow(prompt_text, request.negative_prompt, request.width, request.height, request.steps, request.seed)
    )
    async with httpx.AsyncClient(timeout=300) as client:
        r = await client.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow})
        r.raise_for_status()
        return {"prompt_id": r.json().get("prompt_id"), "type": "video" if is_video else "image"}


async def _generate_via_fal(request: GenerateRequest) -> dict:
    """fal.ai free tier — FLUX schnell (imágenes) o Kling (video)."""
    if not FAL_API_KEY:
        raise ValueError("FAL_API_KEY not set")

    prompt_text = WORKFLOW_PROMPTS.get(request.workflow, "{prompt}").format(
        artist_name=request.artist_name or "artista",
        prompt=request.prompt,
    )

    is_video = request.workflow == "promo_video"
    endpoint = "fal-ai/kling-video/v1.6/standard/text-to-video" if is_video else "fal-ai/flux/schnell"

    payload = {"prompt": prompt_text}
    if not is_video:
        payload.update({
            "image_size": {"width": request.width, "height": request.height},
            "num_inference_steps": request.steps,
            "num_images": 1,
        })
    else:
        payload.update({"duration": "5", "aspect_ratio": "16:9"})

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"https://queue.fal.run/{endpoint}",
            headers={"Authorization": f"Key {FAL_API_KEY}", "Content-Type": "application/json"},
            json=payload,
        )
        r.raise_for_status()
        data = r.json()
        request_id = data.get("request_id", "")

        # Poll result (max 30s)
        for _ in range(10):
            import asyncio
            await asyncio.sleep(3)
            poll = await client.get(
                f"https://queue.fal.run/{endpoint}/requests/{request_id}",
                headers={"Authorization": f"Key {FAL_API_KEY}"},
            )
            result = poll.json()
            if result.get("status") == "COMPLETED":
                if is_video:
                    return {"url": result["output"]["video"]["url"], "type": "video"}
                else:
                    return {"url": result["output"]["images"][0]["url"], "type": "image"}

        return {"url": None, "request_id": request_id, "status": "processing"}


@app.post("/generate", response_model=GenerateResponse)
async def generate_visual(request: GenerateRequest):
    job_id = str(uuid.uuid4())

    # Layer 1: ComfyUI local
    try:
        result = await _generate_via_comfyui(request)
        return GenerateResponse(
            job_id=job_id,
            status="queued",
            message=f"ComfyUI — prompt_id: {result.get('prompt_id', 'unknown')}",
        )
    except Exception:
        pass

    # Layer 2: fal.ai (free tier)
    try:
        result = await _generate_via_fal(request)
        return GenerateResponse(
            job_id=job_id,
            status="completed" if result.get("url") else "processing",
            image_url=result.get("url"),
            message=f"fal.ai — {result.get('type','image')} generado" if result.get("url") else f"fal.ai procesando — request_id: {result.get('request_id')}",
        )
    except Exception as e:
        pass

    # Layer 3: placeholder mock
    return GenerateResponse(
        job_id=job_id,
        status="mock",
        image_url=f"https://placehold.co/{request.width}x{request.height}/1a1a2e/gold?text={request.artist_name or 'ABE+Music'}",
        message="Mock — agrega FAL_API_KEY en .env para generación real (fal.ai free tier disponible en fal.ai/dashboard)",
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
        "fal_configured": bool(FAL_API_KEY),
        "note": "Obtén tu FAL_API_KEY gratis en https://fal.ai/dashboard",
    }
