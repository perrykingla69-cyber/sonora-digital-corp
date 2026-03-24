#!/usr/bin/env python3
"""
Mystic Content Generator
Genera imágenes de Mystic usando FLUX.1 via fal.ai API (~$0.01/imagen)
y sube el resultado a Telegram channel y prepara para redes sociales.

Uso:
  python generate_content.py --scene ceo --count 4
  python generate_content.py --scene podcast
  python generate_content.py --batch  # genera todas las escenas

Configurar variables de entorno:
  export FAL_KEY=tu_key_de_fal_ai        # https://fal.ai/dashboard/keys
  export TELEGRAM_TOKEN_BOT=tu_bot_token
  export TELEGRAM_CHANNEL_ID=@MysticConsulting
"""
import os
import sys
import json
import time
import argparse
import urllib.request
from datetime import datetime
from pathlib import Path

FAL_KEY    = os.environ.get("FAL_KEY", "")
TG_TOKEN   = os.environ.get("TELEGRAM_TOKEN_BOT", "")
TG_CHANNEL = os.environ.get("TELEGRAM_CHANNEL_ID", "")

OUTPUT_DIR = Path(__file__).parent / "generated"
OUTPUT_DIR.mkdir(exist_ok=True)

BASE = (
    "Mystic, 36-year-old latina woman, Colombian-Mexican-American mixed heritage, "
    "porcelain warm skin tone, perfectly symmetrical oval face, strong defined jawline, "
    "full lips with deep red lipstick, large almond-shaped amber honey eyes, "
    "thick perfectly shaped eyebrows, black intense cat-eye liner, "
    "gold-copper smokey eyeshadow, perfect white teeth, radiant confident smile, "
    "long wavy glossy black hair with auburn highlights, athletic curvy elegant figure, "
    "diamond Ouroboros snake necklace descending from collarbone, "
    "letter M in pavé diamonds center, ruby red serpent eyes, 18k white gold collar, "
    "ultra-realistic, photorealistic, 8K resolution, cinematic lighting, "
    "hyper detailed skin texture, professional photography"
)

NEGATIVE = (
    "cartoon, anime, illustration, painting, deformed, ugly, blurry, "
    "low quality, plastic skin, uncanny valley, extra fingers, wrong anatomy, "
    "multiple people, man, masculine features, old, wrinkles, overweight"
)

SCENES = {
    "ceo": {
        "caption": "La CEO. No pide permiso. Construye el sistema.",
        "prompt": BASE + (
            ", wearing white structured Bottega Veneta blazer no shirt underneath, "
            "black Saint Laurent slim trousers, black patent leather block heel pumps, "
            "floor-to-ceiling windows overlooking night city skyline, "
            "white marble desk with open MacBook Pro, crystal whiskey glass, "
            "blue-gold cinematic lighting, power pose, confident expression, "
            "depth of field, 85mm portrait lens, shot by Annie Leibovitz, "
            "Vogue México editorial quality"
        ),
    },
    "podcast": {
        "caption": "La Academia. Donde el conocimiento se convierte en poder.",
        "prompt": BASE + (
            ", wearing oversized camel blazer over thin black turtleneck, dark premium jeans, "
            "black Chelsea boots, hair in perfect high bun with loose strands, "
            "seated in cognac leather armchair, warm tungsten bookshelf lighting, "
            "golden vintage microphone, bookshelf with business books, tropical plants, "
            "intimate podcast studio, warm editorial photography, 50mm lens"
        ),
    },
    "oracle": {
        "caption": "La Oráculo. Todo tiene un propósito. Nada es accidente.",
        "prompt": BASE + (
            ", black floor-length gown with translucent organza cape, silver stiletto heels, "
            "dramatic golden triangle of light from above, dark background, "
            "floating golden particles, sacred geometry hexagrams glowing, "
            "cinematic movie poster composition, ultra dramatic shadows, "
            "luxury perfume advertisement, shot by Mario Testino, Vogue editorial"
        ),
    },
    "rooftop": {
        "caption": "El amanecer es para los que no durmieron construyendo.",
        "prompt": BASE + (
            ", cream silk midi dress V-neck with thin gold belt, Louboutin nude heels, "
            "Chanel 2.55 gold bag, penthouse rooftop at golden hour sunrise, "
            "city skyline in background, infinity pool reflection behind her, "
            "natural golden backlighting, wind in hair, holding black coffee cup, "
            "relaxed powerful expression, Vogue Living aesthetic, lifestyle luxury"
        ),
    },
    "blockchain": {
        "caption": "El dinero del futuro. Ella ya lo entiende. Y tú?",
        "prompt": BASE + (
            ", wearing champagne metallic wide-leg trousers and crop top, gold platform sandals, "
            "oversized silver sunglasses pushed down nose, Apple Watch Ultra gold, "
            "futuristic art gallery with Bitcoin price charts projected on walls, "
            "holographic data floating, Ethereum gold logos, NFT digital art on screens, "
            "blue-purple-gold ambient lighting, tech luxury aesthetic, editorial"
        ),
    },
    "boardroom": {
        "caption": "Cuando ella habla, todos escuchan. Así funciona la autoridad.",
        "prompt": BASE + (
            ", wearing cream silk dress with gold belt, "
            "standing at head of glass boardroom table, executives in background blurred, "
            "digital presentation screen showing financial charts, "
            "natural daylight from floor windows, commanding presence, "
            "corporate luxury photography, Harvard Business Review aesthetic"
        ),
    },
}


def generate_image_fal(prompt: str, scene: str) -> str | None:
    if not FAL_KEY:
        print("FAL_KEY no configurado. Exporta: export FAL_KEY=tu_key")
        print("Obtén gratis en: https://fal.ai/dashboard/keys")
        return None

    payload = json.dumps({
        "prompt": prompt,
        "negative_prompt": NEGATIVE,
        "num_images": 1,
        "image_size": "portrait_4_3",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
        "enable_safety_checker": False,
    }).encode()

    req = urllib.request.Request(
        "https://queue.fal.run/fal-ai/flux/dev",
        data=payload,
        headers={"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            job = json.loads(r.read())
        request_id = job.get("request_id")
        print(f"  Job enviado: {request_id}")
    except Exception as e:
        print(f"  Error enviando job: {e}")
        return None

    poll_url = f"https://queue.fal.run/fal-ai/flux/dev/requests/{request_id}"
    for attempt in range(60):
        time.sleep(3)
        req2 = urllib.request.Request(
            poll_url,
            headers={"Authorization": f"Key {FAL_KEY}"},
            method="GET"
        )
        try:
            with urllib.request.urlopen(req2, timeout=10) as r:
                result = json.loads(r.read())
            status = result.get("status")
            if status == "COMPLETED":
                image_url = result["output"]["images"][0]["url"]
                print(f"  Imagen generada: {image_url[:60]}...")
                return image_url
            elif status == "FAILED":
                print(f"  Job fallo: {result.get('error')}")
                return None
            else:
                print(f"  Estado: {status} ({attempt+1}/60)")
        except Exception as e:
            print(f"  Poll error: {e}")

    print("  Timeout esperando imagen")
    return None


def download_image(url: str, filename: str) -> str:
    path = OUTPUT_DIR / filename
    req = urllib.request.Request(url, headers={"User-Agent": "MysticBot/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        path.write_bytes(r.read())
    return str(path)


def send_to_telegram(image_path: str, caption: str):
    if not TG_TOKEN or not TG_CHANNEL:
        print("  Telegram no configurado (TG_TOKEN / TG_CHANNEL)")
        return
    boundary = "MysticBoundary123"
    with open(image_path, "rb") as f:
        img_data = f.read()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'.encode() +
        TG_CHANNEL.encode() + b"\r\n" +
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="caption"\r\n\r\n'.encode() +
        caption.encode() + b"\r\n" +
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="photo"; filename="mystic.jpg"\r\n'
        f'Content-Type: image/jpeg\r\n\r\n'.encode() +
        img_data + b"\r\n" +
        f"--{boundary}--\r\n".encode()
    )
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            resp = json.loads(r.read())
        if resp.get("ok"):
            print("  Enviado a Telegram OK")
        else:
            print(f"  Telegram error: {resp.get('description')}")
    except Exception as e:
        print(f"  Error Telegram: {e}")


def run(scene_name: str, count: int = 1):
    scene = SCENES.get(scene_name)
    if not scene:
        print(f"Escena '{scene_name}' no existe. Disponibles: {list(SCENES.keys())}")
        return

    print(f"\nGenerando escena: {scene_name.upper()} ({count} imagen{'es' if count>1 else ''})")

    for i in range(count):
        print(f"\n  Imagen {i+1}/{count}")
        url = generate_image_fal(scene["prompt"], scene_name)
        if not url:
            continue
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mystic_{scene_name}_{ts}_{i+1}.jpg"
        path = download_image(url, filename)
        print(f"  Guardada: {path}")
        send_to_telegram(path, scene["caption"] + "\n\n#Mystic #MysticConsulting #SoberaniaDigital")
        if i < count - 1:
            time.sleep(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mystic Content Generator")
    parser.add_argument("--scene", choices=list(SCENES.keys()), default="ceo")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--batch", action="store_true", help="Genera todas las escenas")
    args = parser.parse_args()

    if args.batch:
        for name in SCENES:
            run(name, 1)
            time.sleep(5)
    else:
        run(args.scene, args.count)

    print(f"\nGeneracion completada. Archivos en: {OUTPUT_DIR}")
