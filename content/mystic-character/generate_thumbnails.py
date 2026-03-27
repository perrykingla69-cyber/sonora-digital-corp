#!/usr/bin/env python3
"""
Generador de Miniaturas YouTube — Estilo Miguel Baena
Mystic como cara del canal HERMES

Estilo: fondo oscuro/degradado dramático, Mystic con expresión intensa,
colores vibrantes (dorado, rojo, verde neón), composición asimétrica,
luz de estudio dramática tipo chiaroscuro — exactamente como Miguel Baena.

Uso:
  python generate_thumbnails.py --video 1
  python generate_thumbnails.py --all
  python generate_thumbnails.py --list

Requiere:
  export HF_TOKEN=hf_...
"""

import os, sys, json, time, argparse, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path

HF_TOKEN = os.environ.get("HF_TOKEN", "")
if not HF_TOKEN:
    print("\n❌ HF_TOKEN no configurada. Ejecuta: export HF_TOKEN=hf_tu_token\n")
    sys.exit(1)

OUTPUT_DIR = Path(__file__).parent / "thumbnails"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Base Mystic para miniaturas — expresión dramática, estilo Miguel Baena ──
BASE_THUMB = (
    "Mystic, 36-year-old latina woman, porcelain warm golden skin, "
    "perfectly symmetrical face, full lips red lipstick, large amber eyes WIDE OPEN shocked expression, "
    "thick perfect eyebrows raised in surprise or intensity, "
    "diamond Ouroboros snake necklace 18k white gold, "
    "ultra-realistic photorealistic 8K, "
    "YouTube thumbnail style Miguel Baena, dramatic chiaroscuro studio lighting, "
    "DARK background with dramatic color gradient, "
    "cinematic bold composition, face occupying LEFT THIRD of frame, "
    "intense direct eye contact with camera, "
    "professional studio photography, sharp focus face, "
    "volumetric light rays, high contrast shadows"
)

NEGATIVE = (
    "cartoon, anime, blurry, low quality, multiple people, text, watermark, "
    "logo, border, frame, ugly, deformed, extra fingers, bad anatomy, "
    "soft lighting, flat lighting, overexposed, washed out"
)

# ── 10 miniaturas — una por video del script TikTok/YouTube ─────────────────
THUMBNAILS = {
    "multa_sat": {
        "video": 1,
        "titulo": "¿Sabes cuánto te puede multar el SAT?",
        "expresion": "shocked, mouth slightly open, eyebrows raised, hand on cheek",
        "fondo": "deep red to black gradient background, red danger light from left",
        "acento": "red alert glow, emergency red lighting",
        "prompt_extra": (
            "wearing black blazer, red emergency lighting from left side, "
            "dark red to black dramatic background, "
            "expression: SHOCKED and alarmed, eyes wide open, "
            "hand raised near face in disbelief"
        ),
        "texto_sugerido": "EL SAT TE PUEDE MULTAR\n¿CUÁNTO? 😱",
    },
    "contador_vs_hermes": {
        "video": 2,
        "titulo": "Tu contador vs HERMES — quién gana",
        "expresion": "confident smirk, one eyebrow raised, arms crossed",
        "fondo": "split dark blue and gold gradient",
        "acento": "gold accent lighting",
        "prompt_extra": (
            "wearing white power blazer, arms crossed confidently, "
            "GOLD dramatic lighting from above right, "
            "dark navy to black background with gold particle effects, "
            "expression: supremely confident, knowing smirk, one eyebrow raised, "
            "power pose, slightly tilted head"
        ),
        "texto_sugerido": "$8,000/mes vs $799\nLA DIFERENCIA 👀",
    },
    "error_mve": {
        "video": 3,
        "titulo": "Este error de aduanas te cuesta $300,000 MXN",
        "expresion": "intense warning look, pointing finger at camera",
        "fondo": "deep orange to black gradient, danger warning atmosphere",
        "acento": "orange warning glow",
        "prompt_extra": (
            "wearing dark blazer, pointing directly at camera with index finger, "
            "ORANGE dramatic warning light from below-left, "
            "dark background with orange glow effect, "
            "expression: INTENSE WARNING, serious eyes, eyebrows furrowed, "
            "mouth slightly open as if saying 'cuidado'"
        ),
        "texto_sugerido": "$300,000 MXN\nEN MULTAS 🚨",
    },
    "dia_17": {
        "video": 4,
        "titulo": "El 17 de cada mes el SAT espera",
        "expresion": "urgent intense stare, leaning forward",
        "fondo": "dark red countdown atmosphere",
        "acento": "red clock urgency lighting",
        "prompt_extra": (
            "wearing deep red blazer, leaning slightly toward camera urgently, "
            "DRAMATIC red side lighting, dark background with red glow, "
            "expression: URGENT intense direct stare, eyebrows slightly raised, "
            "lips pressed together in urgency"
        ),
        "texto_sugerido": "DÍA 17\n¿ESTÁS LISTO? ⏰",
    },
    "bot_2am": {
        "video": 5,
        "titulo": "Le pregunté a HERMES a las 2am",
        "expresion": "amazed wide eyes, hand covering mouth in disbelief",
        "fondo": "dark blue night atmosphere, phone screen glow",
        "acento": "blue tech glow from smartphone",
        "prompt_extra": (
            "wearing casual luxury black top, holding smartphone with BRIGHT SCREEN, "
            "phone light illuminating face from below creating dramatic shadow, "
            "dark midnight blue background, "
            "expression: AMAZED disbelief, eyes WIDE, hand near mouth, "
            "eyebrows raised extremely high"
        ),
        "texto_sugerido": "2AM Y HERMES\nME RESPONDIÓ 🤖",
    },
    "resico": {
        "video": 6,
        "titulo": "RESICO — el dinero que te estás perdiendo",
        "expresion": "money-face expression, rubbing fingers together gesture",
        "fondo": "dark green to black gradient, money energy",
        "acento": "green money glow, gold particle rain",
        "prompt_extra": (
            "wearing emerald green blazer, rubbing thumb and fingers together 'money' gesture, "
            "GREEN and GOLD dramatic lighting, "
            "dark background with green glow and gold shimmer particles, "
            "expression: knowing smile with raised eyebrow, 'you're missing out' look"
        ),
        "texto_sugerido": "RESICO:\nESTÁS DEJANDO\nDINERO 💚",
    },
    "nomina": {
        "video": 7,
        "titulo": "Nómina en 10 segundos — demo en vivo",
        "expresion": "excited confident smile, thumbs up",
        "fondo": "dark tech blue background, speed lines",
        "acento": "electric blue speed effect",
        "prompt_extra": (
            "wearing sharp navy blazer, thumbs up gesture, big confident smile, "
            "ELECTRIC BLUE dramatic lighting with speed motion blur in background, "
            "dark background with blue digital data streams, "
            "expression: excited genuine confidence, wide smile, "
            "slight lean forward energy"
        ),
        "texto_sugerido": "NÓMINA EN\n10 SEGUNDOS ⚡",
    },
    "oferta_fundador": {
        "video": 8,
        "titulo": "Oferta fundador se acaba — 1 de Abril",
        "expresion": "urgent pointing at viewer, serious warning face",
        "fondo": "black with gold countdown clock energy",
        "acento": "gold urgency glow, timer energy",
        "prompt_extra": (
            "wearing all-black power outfit, pointing DIRECTLY at camera with both hands, "
            "GOLD and white dramatic lighting from above, "
            "pitch black background with gold glow and timer light effects, "
            "expression: URGENT serious direct stare, eyebrows slightly furrowed, "
            "mouth forming warning expression"
        ),
        "texto_sugerido": "SE ACABA\nEL 1 DE ABRIL 🔴\nPRECIO FUNDADOR",
    },
    "cfdi": {
        "video": 9,
        "titulo": "El SAT ya usa IA para revisar tus CFDIs",
        "expresion": "suspicious intense look, one eyebrow raised",
        "fondo": "dark surveillance atmosphere, green matrix data",
        "acento": "green matrix surveillance glow",
        "prompt_extra": (
            "wearing dark blazer, head slightly tilted, suspicious intense expression, "
            "GREEN surveillance/matrix digital light from above, "
            "dark background with green data streams and code rain effect, "
            "expression: SUSPICIOUS serious intensity, one eyebrow raised, "
            "narrowed eyes as if analyzing"
        ),
        "texto_sugerido": "EL SAT USA IA\nPARA VERTE 👁️",
    },
    "cierre_mensual": {
        "video": 10,
        "titulo": "Cierre contable automático — sin llamar al contador",
        "expresion": "relaxed powerful smile, leaning back confidently",
        "fondo": "luxury dark office environment",
        "acento": "warm gold executive lighting",
        "prompt_extra": (
            "wearing premium white blazer, relaxed confident posture leaning back slightly, "
            "WARM GOLD executive lighting from right, luxury dark background, "
            "expression: POWERFUL relaxed smile, completely in control, "
            "slight head tilt of confidence, Mona Lisa quality of mystery and power"
        ),
        "texto_sugerido": "CIERRE MENSUAL\nEN AUTOMÁTICO ✅",
    },
}


def generate_thumbnail(key: str) -> str | None:
    t = THUMBNAILS[key]
    prompt = (
        BASE_THUMB + ", " + t["prompt_extra"] +
        ", YouTube thumbnail 16:9 aspect ratio, "
        "composed for text overlay on RIGHT SIDE of frame"
    )
    payload = json.dumps({"inputs": prompt[:500]}).encode()
    req = urllib.request.Request(
        "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell",
        data=payload,
        headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
        method="POST"
    )
    print(f"  Generando miniatura: {t['titulo'][:50]}...")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            image_data = r.read()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"thumb_v{t['video']:02d}_{key}_{ts}.jpg"
        path = OUTPUT_DIR / filename
        path.write_bytes(image_data)
        # Guardar texto sugerido para overlay
        txt_path = OUTPUT_DIR / f"thumb_v{t['video']:02d}_{key}_{ts}_texto.txt"
        txt_path.write_text(
            f"VIDEO #{t['video']}: {t['titulo']}\n\n"
            f"TEXTO EN MINIATURA:\n{t['texto_sugerido']}\n\n"
            f"EXPRESIÓN: {t['expresion']}\n"
            f"FONDO: {t['fondo']}\n"
            f"ACENTO: {t['acento']}\n",
            encoding="utf-8"
        )
        print(f"  ✅ Guardada: {filename}")
        print(f"  📝 Texto overlay: {t['texto_sugerido'].replace(chr(10), ' | ')}")
        return str(path)
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def list_thumbnails():
    print("\n🎬 MINIATURAS YOUTUBE — HERMES (estilo Miguel Baena)\n")
    for key, t in THUMBNAILS.items():
        print(f"  Video #{t['video']:2d} [{key}]")
        print(f"           {t['titulo']}")
        print(f"           Texto: {t['texto_sugerido'].replace(chr(10), ' | ')}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de Miniaturas YouTube — HERMES")
    parser.add_argument("--video", type=int, help="Número de video (1-10)")
    parser.add_argument("--all", action="store_true", help="Genera las 10 miniaturas")
    parser.add_argument("--list", action="store_true", help="Lista todas las miniaturas")
    args = parser.parse_args()

    if args.list:
        list_thumbnails()
        sys.exit(0)

    keys = list(THUMBNAILS.keys())

    if args.all:
        print(f"\n🚀 Generando 10 miniaturas estilo Miguel Baena...\n")
        for key in keys:
            generate_thumbnail(key)
            time.sleep(3)
    elif args.video:
        match = [k for k, t in THUMBNAILS.items() if t["video"] == args.video]
        if not match:
            print(f"Video #{args.video} no encontrado. Usa --list para ver opciones.")
            sys.exit(1)
        generate_thumbnail(match[0])
    else:
        parser.print_help()

    print(f"\n✅ Miniaturas en: {OUTPUT_DIR}")
    print("💡 Abre las imágenes y agrega el texto con Canva o CapCut")
