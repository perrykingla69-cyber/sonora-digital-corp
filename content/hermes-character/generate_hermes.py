#!/usr/bin/env python3
"""
Hermes Content Generator
Genera imágenes de Hermes usando FLUX.1-schnell via HuggingFace Inference API (gratis con token HF)
y sube el resultado a Telegram channel y prepara para redes sociales.

Uso:
  python generate_hermes.py --scene empresario --count 4
  python generate_hermes.py --scene cierre
  python generate_hermes.py --batch  # genera todas las escenas
  python generate_hermes.py --list   # muestra escenas disponibles con captions

Configurar variables de entorno:
  export HF_TOKEN=hf_tu_token              # https://huggingface.co/settings/tokens
  export TELEGRAM_TOKEN_BOT=tu_bot_token
  export TELEGRAM_CHANNEL_ID=@HermesAI
"""
import os
import sys
import json
import time
import argparse
import urllib.request
from datetime import datetime
from pathlib import Path

# ── HuggingFace Inference API — gratis con token HF ─────────────────────────
# Token gratis en: https://huggingface.co/settings/tokens (Read token)
HF_TOKEN = os.environ.get("HF_TOKEN", "")
if not HF_TOKEN:
    print()
    print("❌ HF_TOKEN no configurada.")
    print("   1. Ve a: https://huggingface.co/settings/tokens")
    print("   2. Crea un token tipo 'Read' (gratis)")
    print("   3. Ejecuta: export HF_TOKEN=hf_tu_token")
    print()
    sys.exit(1)

TG_TOKEN   = os.environ.get("TELEGRAM_TOKEN_BOT", "")
TG_CHANNEL = os.environ.get("TELEGRAM_CHANNEL_ID", "")

OUTPUT_DIR = Path(__file__).parent / "generated"
OUTPUT_DIR.mkdir(exist_ok=True)

BASE = (
    "Hermes, 36-year-old European Mediterranean man, Spanish-Italian-Greek heritage, "
    "1.86m tall corpulent athletic build, wide shoulders broad chest defined biceps and triceps, "
    "sharp chiseled square jawline, high defined cheekbones, perfectly symmetrical perfilada face, "
    "large dominant deep green or amber eyes, thick pronounced arched eyebrows his trademark feature, "
    "closed perfectly groomed beard 4mm, dense mustache, large full defined lips, "
    "perfect straight white teeth captivating smile, "
    "dark black-brown European classic volume hairstyle, "
    "diamond eye of Hermes triangle lapel pin gold, "
    "ultra-realistic photorealistic 8K, cinematic lighting, "
    "hyper detailed skin texture, professional photography, "
    "Vogue Hombre editorial quality, powerful masculine energy"
)

NEGATIVE = (
    "cartoon, anime, illustration, painting, deformed, ugly, blurry, "
    "low quality, plastic skin, uncanny valley, extra fingers, wrong anatomy, "
    "multiple people, woman, feminine features, old, wrinkles, overweight, "
    "casual clothes, t-shirt, hoodie, sneakers"
)

SCENES = {
    "empresario": {
        "caption": "El Empresario. No pide permiso. Construye el legado.",
        "prompt": BASE + (
            ", white fitted V-neck dress shirt hugging chest and biceps, "
            "dark navy tailored European suit jacket, silk diagonal stripe tie burgundy-navy, "
            "black leather suspenders visible over shirt, tailored dress trousers, "
            "black patent leather oxford shoes, "
            "floor-to-ceiling windows overlooking night city skyline, "
            "blue-gold cinematic lighting, power stance arms relaxed, "
            "confident dominant expression, depth of field 85mm portrait lens, "
            "Vogue Hombre editorial, GQ México quality"
        ),
        "instagram_caption": (
            "No se trata de trabajar más. Se trata de trabajar con inteligencia.\n\n"
            "HERMES automatiza tu contabilidad para que tú te enfoques en lo que importa: "
            "construir tu empresa.\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#EmpresariosMX #LiderazgoMX #AutomatizacionMX"
        ),
    },
    "cierre": {
        "caption": "El Cierre. Cuando la pluma toca el papel, ya todo estaba ganado.",
        "prompt": BASE + (
            ", three-piece Oxford grey suit impeccably tailored, "
            "burgundy silk tie, white pocket square folded in peak, "
            "classic gold-steel dress watch, black oxford shoes mirror shine, "
            "signing contract on white marble table, Montblanc pen, "
            "executive documents spread on table, mahogany boardroom, "
            "warm dramatic overhead lighting, "
            "satisfied authority expression, shallow depth of field, "
            "GQ editorial corporate photography"
        ),
        "instagram_caption": (
            "Cada firma es el resultado de meses de trabajo invisible.\n\n"
            "Con HERMES, ese trabajo invisible ya está automatizado — "
            "cierres mensuales, declaraciones, nómina. Todo al día.\n\n"
            "Tú solo firma.\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#CierresFiscales #ContabilidadAutomatica #DirectivosMX"
        ),
    },
    "visionario": {
        "caption": "El Visionario. El futuro no se predice. Se construye.",
        "prompt": BASE + (
            ", black fitted V-neck shirt, black silk bow tie, satin lapel dinner jacket, "
            "gold pocket watch chain across chest, "
            "futuristic art gallery background with financial data projections on walls, "
            "dark ambiance with gold and blue accent lighting, "
            "standing with composed confidence, slight smile, "
            "golden particles floating in air, "
            "editorial night gala atmosphere, dramatic cinematic quality"
        ),
        "instagram_caption": (
            "Los datos de tu empresa ya tienen la respuesta. ¿La estás leyendo?\n\n"
            "HERMES analiza tu situación fiscal en tiempo real. "
            "Tú tomas las decisiones, nosotros ponemos la inteligencia.\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#VisionEmpresarial #InteligenciaArtificial #TransformacionDigital"
        ),
    },
    "mentor": {
        "caption": "El Mentor. Cuando dominas tus números, nadie te puede engañar.",
        "prompt": BASE + (
            ", white fitted V-neck shirt with black suspenders only no jacket, "
            "grey tailored trousers, brown oxford shoes, "
            "sleeves rolled to elbows showing defined forearms, "
            "standing in modern conference room, "
            "large digital screen behind showing financial dashboard with charts, "
            "HERMES AI data visualizations on screen, "
            "pointing at financial data with authority, "
            "warm professional lighting, approachable confident expression, "
            "editorial corporate photography, GQ business style"
        ),
        "instagram_caption": (
            "La mayoría de los dueños de negocio no entienden sus propios números.\n\n"
            "Con HERMES, eso cambia — reportes claros, alertas automáticas, "
            "sin jerga contable. Tú metes decisiones, el sistema mete la lógica.\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#EducacionFinanciera #NegociosMX #MentorEmpresarial"
        ),
    },
    "dominio": {
        "caption": "El Dominio. Desde aquí arriba, todo se ve con claridad.",
        "prompt": BASE + (
            ", white fitted V-neck dress shirt, dark tailored suit jacket, "
            "silk tie, black suspenders, "
            "standing at edge of skyscraper rooftop terrace, "
            "looking slightly downward toward camera, dominant perspective, "
            "massive city skyline stretching behind him at night, "
            "city lights reflecting in his eyes, "
            "blue-gold cinematic lighting from below, "
            "ultra-cinematic composition, power shot, "
            "editorial GQ Hombre photography"
        ),
        "instagram_caption": (
            "No es arrogancia. Es perspectiva.\n\n"
            "Cuando tienes tus finanzas bajo control, "
            "ves el negocio desde otra altura.\n\n"
            "HERMES te da esa vista aérea — en tiempo real.\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#VisionEstrategica #LiderazgoMX #CrecimientoEmpresarial"
        ),
    },
    "sat_warning_h": {
        "caption": "El SAT no espera. Hermes tampoco.",
        "prompt": BASE + (
            ", white fitted V-neck dress shirt, dark tailored suit jacket, "
            "silk tie, black suspenders, "
            "pointing directly at camera with serious warning expression, "
            "dark command center background with red and black tones, "
            "holographic SAT compliance dashboards in red floating behind him, "
            "fiscal data alerts and charts in air, "
            "dramatic red-black-gold cinematic lighting, "
            "ultra dramatic atmosphere, urgent powerful energy, "
            "8K editorial photography"
        ),
        "instagram_caption": (
            "El SAT no manda recordatorios amables. Manda multas y requerimientos.\n\n"
            "Con HERMES, tus declaraciones, complementos de pago y cierres fiscales "
            "están al día — automáticamente. Sin sorpresas. Sin multas.\n\n"
            "¿Cuándo fue la última vez que revisaste tu situación fiscal?\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#SAT2024 #DeclaracionesSAT #CumplimientoFiscal #MultasSAT"
        ),
    },
}


def list_scenes():
    """Muestra todas las escenas disponibles con su caption e instagram caption."""
    print()
    print("=" * 60)
    print("  ESCENAS DISPONIBLES — Hermes Content Generator")
    print("=" * 60)
    for name, data in SCENES.items():
        print(f"\n  [{name.upper()}]")
        print(f"  Caption: {data['caption']}")
        print(f"  Instagram:")
        lines = data['instagram_caption'].split('\n')
        for line in lines[:3]:
            print(f"    {line}")
        if len(lines) > 3:
            print(f"    (...)")
    print()
    print(f"  Total: {len(SCENES)} escenas")
    print()
    print("  Uso:")
    print("    python generate_hermes.py --scene <nombre>")
    print("    python generate_hermes.py --batch")
    print()


def generate_image_hf(prompt: str, scene: str) -> str | None:
    """Genera imagen via HuggingFace Inference API — gratis con token HF."""
    payload = json.dumps({"inputs": prompt[:500]}).encode()
    req = urllib.request.Request(
        "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell",
        data=payload,
        headers={
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST"
    )
    print(f"  Generando con HuggingFace FLUX.1-schnell (gratis)...")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            image_data = r.read()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        seed = int(time.time()) % 99999
        filename = f"hermes_{scene}_{ts}_{seed}.jpg"
        path = OUTPUT_DIR / filename
        path.write_bytes(image_data)
        print(f"  ✅ Imagen guardada: {filename}")
        return str(path)
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def send_to_telegram(image_path: str, caption: str):
    if not TG_TOKEN or not TG_CHANNEL:
        print("  Telegram no configurado (TG_TOKEN / TG_CHANNEL) — omitiendo envío")
        return
    boundary = "HermesBoundary456"
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
        f'Content-Disposition: form-data; name="photo"; filename="hermes.jpg"\r\n'
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
            print("  ✅ Enviado a Telegram OK")
        else:
            print(f"  ⚠️  Telegram error: {resp.get('description')}")
    except Exception as e:
        print(f"  ⚠️  Error Telegram: {e}")


def run(scene_name: str, count: int = 1):
    scene = SCENES.get(scene_name)
    if not scene:
        print(f"Escena '{scene_name}' no existe. Disponibles: {list(SCENES.keys())}")
        return

    print(f"\nGenerando escena: {scene_name.upper()} ({count} imagen{'es' if count > 1 else ''})")
    print(f"  Caption: {scene['caption']}")

    for i in range(count):
        print(f"\n  Imagen {i+1}/{count}")
        path = generate_image_hf(scene["prompt"], scene_name)
        if not path:
            continue
        print(f"  Guardada: {path}")

        # Guardar instagram caption en archivo de texto junto a la imagen
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        caption_file = OUTPUT_DIR / f"hermes_{scene_name}_{ts}_{i+1}_caption.txt"
        caption_file.write_text(scene["instagram_caption"], encoding="utf-8")
        print(f"  Caption IG guardada: {caption_file.name}")

        send_to_telegram(path, scene["caption"] + "\n\n#HermesAI #ContabilidadMX #PYMEsMexicanas")
        if i < count - 1:
            time.sleep(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hermes Content Generator — HERMES AI OS")
    parser.add_argument("--scene", choices=list(SCENES.keys()), default="empresario",
                        help="Escena a generar")
    parser.add_argument("--count", type=int, default=1,
                        help="Número de variaciones")
    parser.add_argument("--batch", action="store_true",
                        help="Genera todas las escenas (1 imagen cada una)")
    parser.add_argument("--list", action="store_true",
                        help="Lista todas las escenas disponibles con sus captions")
    args = parser.parse_args()

    if args.list:
        list_scenes()
        sys.exit(0)

    if args.batch:
        for name in SCENES:
            run(name, 1)
            time.sleep(5)
    else:
        run(args.scene, args.count)

    print(f"\nGeneracion completada. Archivos en: {OUTPUT_DIR}")
