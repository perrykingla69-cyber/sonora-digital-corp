#!/usr/bin/env python3
"""
Mystic Content Generator
Genera imágenes de Mystic usando FLUX.1 via fal.ai API (~$0.01/imagen)
y sube el resultado a Telegram channel y prepara para redes sociales.

Uso:
  python generate_content.py --scene ceo --count 4
  python generate_content.py --scene podcast
  python generate_content.py --batch  # genera todas las escenas
  python generate_content.py --list   # muestra escenas disponibles con captions

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
        "instagram_caption": (
            "No esperes que alguien te dé el trono. Constrúyelo.\n\n"
            "HERMES automatiza tu contabilidad para que tú te enfoques en lo que importa: "
            "crecer tu empresa.\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#CEOMexicana #EmprendedoresMX #LiderazgoFemenino"
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
        "instagram_caption": (
            "El conocimiento que no se aplica no sirve de nada.\n\n"
            "Con HERMES, cada dueño de negocio entiende sus finanzas — sin ser contador.\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#EducacionFinanciera #NegociosMX #EmprendimientoMX"
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
        "instagram_caption": (
            "Los números de tu empresa ya tienen la respuesta. ¿La estás leyendo?\n\n"
            "HERMES analiza tu situación fiscal en tiempo real. Tú tomas las decisiones, "
            "nosotros ponemos la inteligencia.\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#DecisionesInteligentes #InteligenciaArtificial #AutomatizacionMX"
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
        "instagram_caption": (
            "Mientras otros duermen, tú estás construyendo.\n\n"
            "HERMES trabaja 24/7 para que tu negocio nunca se detenga — facturas, "
            "cierres, nómina. Todo automatizado.\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#AutomatizacionContable #MindsetEmprendedor #GrindMX"
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
        "instagram_caption": (
            "El futuro de las finanzas ya llegó. ¿Tu empresa está lista?\n\n"
            "HERMES integra tecnología de punta para que tus PYMEs operen como Fortune 500.\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#FinTechMX #TransformacionDigital #TecnologiaFinanciera"
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
        "instagram_caption": (
            "La sala de juntas es tuya cuando dominas tus números.\n\n"
            "HERMES te da reportes financieros claros, sin jerga contable. "
            "Entra a cada reunión con todo el poder.\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#ReportesFinancieros #GestionEmpresarial #DirectivosMX"
        ),
    },
    "sat_warning": {
        "caption": "El SAT no espera. Tú tampoco deberías.",
        "prompt": BASE + (
            ", power CEO look with sharp black structured blazer and deep red blouse, "
            "standing before massive holographic control panel with fiscal data dashboards, "
            "SAT compliance charts in red and gold floating in air, "
            "dark command center ambiance with red accent lighting, "
            "golden data streams flowing around her, calculated alert expression, "
            "one hand on holographic interface, futuristic tax control room, "
            "cinematic red-gold-black color palette, ultra dramatic atmosphere, "
            "8K editorial photography"
        ),
        "instagram_caption": (
            "El SAT no manda recordatorios simpáticos. Manda multas.\n\n"
            "Con HERMES, tus declaraciones, complementos y cierres fiscales están al día — "
            "automáticamente. Sin sorpresas. Sin multas.\n\n"
            "¿Cuándo fue la última vez que revisaste tu situación fiscal?\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#SAT2024 #DeclaracionesSAT #CumplimientoFiscal #MultasSAT"
        ),
    },
    "whatsapp_demo": {
        "caption": "Tu contador en WhatsApp. 24/7. Sin excusas.",
        "prompt": BASE + (
            ", casual-power style: fitted premium charcoal blazer over white fitted tee, "
            "dark slim jeans, white sneakers, hair down relaxed waves, "
            "holding latest iPhone with WhatsApp chat interface visible on screen, "
            "showing conversation with HERMES AI financial assistant, "
            "modern co-working space background with warm bokeh lighting, "
            "golden hour natural light, approachable confident smile, "
            "lifestyle tech photography, 35mm editorial lens"
        ),
        "instagram_caption": (
            "¿Necesitas saber tu saldo de IVA a las 11pm? Pregúntale a HERMES por WhatsApp.\n\n"
            "Sin esperar al contador. Sin abrir Excel. Sin estrés.\n\n"
            "HERMES responde en segundos con información real de tu empresa — "
            "facturas, gastos, cierres, todo desde tu celular.\n\n"
            "Conoce HERMES en sonoradigitalcorp.com 🔗 en bio\n\n"
            "#HermesAI #ContabilidadMX #PYMEsMexicanas #SAT #IA #FinanzasMX "
            "#WhatsAppBusiness #ContadorDigital #FinanzasEnTuCelular"
        ),
    },
}


def list_scenes():
    """Muestra todas las escenas disponibles con su caption e instagram caption."""
    print()
    print("=" * 60)
    print("  ESCENAS DISPONIBLES — Mystic Content Generator")
    print("=" * 60)
    for name, data in SCENES.items():
        print(f"\n  [{name.upper()}]")
        print(f"  Caption: {data['caption']}")
        print(f"  Instagram:")
        # Mostrar primeras dos líneas del instagram caption
        lines = data['instagram_caption'].split('\n')
        for line in lines[:3]:
            print(f"    {line}")
        if len(lines) > 3:
            print(f"    (...)")
    print()
    print(f"  Total: {len(SCENES)} escenas")
    print()
    print("  Uso:")
    print("    python generate_content.py --scene <nombre>")
    print("    python generate_content.py --batch")
    print()


def generate_image_fal(prompt: str, scene: str) -> str | None:
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
    print(f"  Generando con HuggingFace FLUX.1 (gratis)...")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            image_data = r.read()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        seed = int(time.time()) % 99999
        filename = f"{scene}_{ts}_{seed}.jpg"
        path = OUTPUT_DIR / filename
        path.write_bytes(image_data)
        print(f"  ✅ Imagen guardada: {filename}")
        return str(path)
    except Exception as e:
        print(f"  Error: {e}")
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
    print(f"  Caption: {scene['caption']}")

    for i in range(count):
        print(f"\n  Imagen {i+1}/{count}")
        path = generate_image_fal(scene["prompt"], scene_name)
        if not path:
            continue
        print(f"  Guardada: {path}")

        # Guardar instagram caption en archivo de texto junto a la imagen
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        caption_file = OUTPUT_DIR / f"mystic_{scene_name}_{ts}_{i+1}_caption.txt"
        caption_file.write_text(scene["instagram_caption"], encoding="utf-8")
        print(f"  Caption IG: {caption_file}")

        send_to_telegram(path, scene["caption"] + "\n\n#HermesAI #ContabilidadMX #PYMEsMexicanas")
        if i < count - 1:
            time.sleep(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mystic Content Generator — HERMES")
    parser.add_argument("--scene", choices=list(SCENES.keys()), default="ceo",
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
