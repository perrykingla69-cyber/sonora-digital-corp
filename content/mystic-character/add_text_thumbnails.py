#!/usr/bin/env python3
"""
Agrega texto estilo Miguel Baena a las miniaturas de Mystic.
Texto bold blanco con sombra negra, lado derecho, fondo semitransparente.

Uso:
  python add_text_thumbnails.py          # procesa todas las miniaturas
  python add_text_thumbnails.py --video 1
"""

import os, sys, glob, argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

THUMBS_DIR = Path(__file__).parent / "thumbnails"
OUT_DIR = Path(__file__).parent / "thumbnails_final"
OUT_DIR.mkdir(exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# Texto por video (del generate_thumbnails.py)
TEXTOS = {
    1:  {"lineas": ["EL SAT TE PUEDE", "MULTAR", "¿CUÁNTO? 😱"],       "color": "#FF3B3B"},
    2:  {"lineas": ["$8,000/MES", "VS $799", "LA DIFERENCIA 👀"],       "color": "#D4AF37"},
    3:  {"lineas": ["$300,000 MXN", "EN MULTAS", "🚨"],                 "color": "#FF6B00"},
    4:  {"lineas": ["DÍA 17", "¿ESTÁS", "LISTO? ⏰"],                   "color": "#FF3B3B"},
    5:  {"lineas": ["2AM Y HERMES", "ME RESPONDIÓ", "🤖"],              "color": "#00CFFF"},
    6:  {"lineas": ["RESICO:", "ESTÁS DEJANDO", "DINERO 💚"],            "color": "#00E676"},
    7:  {"lineas": ["NÓMINA EN", "10 SEGUNDOS", "⚡"],                  "color": "#00CFFF"},
    8:  {"lineas": ["SE ACABA", "EL 1 DE ABRIL", "PRECIO FUNDADOR 🔴"], "color": "#D4AF37"},
    9:  {"lineas": ["EL SAT USA IA", "PARA VERTE", "👁️"],               "color": "#00E676"},
    10: {"lineas": ["CIERRE MENSUAL", "EN AUTOMÁTICO", "✅"],            "color": "#D4AF37"},
}

def add_text(img_path: str, video_num: int) -> str:
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size

    # Redimensionar a 1280x720 si no lo es
    if (w, h) != (1280, 720):
        img = img.resize((1280, 720), Image.LANCZOS)
        w, h = 1280, 720

    draw = ImageDraw.Draw(img)
    texto = TEXTOS.get(video_num)
    if not texto:
        return img_path

    # Overlay oscuro en lado derecho para legibilidad del texto
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rectangle([w // 2, 0, w, h], fill=(0, 0, 0, 140))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # Escribir líneas de texto
    lineas = texto["lineas"]
    color_acento = texto["color"]
    x_start = w // 2 + 30
    y_start = h // 4

    for i, linea in enumerate(lineas):
        # Tamaño de fuente dinámico
        if i == 0:
            size = 72
        elif i == 1:
            size = 80
        else:
            size = 60

        try:
            font = ImageFont.truetype(FONT_BOLD, size)
        except:
            font = ImageFont.load_default()

        # Color: primera línea blanca, segunda en color acento, tercera blanca
        color = "white" if i != 1 else color_acento

        y = y_start + i * (size + 15)

        # Sombra (4 offsets para grosor)
        for ox, oy in [(-3,-3),(3,-3),(-3,3),(3,3),(0,4),(4,0),(-4,0),(0,-4)]:
            draw.text((x_start + ox, y + oy), linea, font=font, fill=(0, 0, 0, 220))

        # Texto principal
        draw.text((x_start, y), linea, font=font, fill=color)

    # Guardar como RGB (sin alpha)
    out = img.convert("RGB")
    out_path = OUT_DIR / f"FINAL_v{video_num:02d}_{Path(img_path).stem}.jpg"
    out.save(str(out_path), "JPEG", quality=95)
    print(f"  ✅ v{video_num:02d} → {out_path.name}")
    return str(out_path)


def procesar_todos():
    print("\n🎬 Agregando texto a miniaturas estilo Miguel Baena...\n")
    for video_num, _ in TEXTOS.items():
        pattern = str(THUMBS_DIR / f"thumb_v{video_num:02d}_*.jpg")
        archivos = sorted(glob.glob(pattern))
        if not archivos:
            print(f"  ⚠️  Video #{video_num} — no encontrado en {pattern}")
            continue
        add_text(archivos[-1], video_num)  # más reciente
    print(f"\n✅ Miniaturas finales en: {OUT_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=int, help="Solo procesar video N")
    args = parser.parse_args()

    if args.video:
        pattern = str(THUMBS_DIR / f"thumb_v{args.video:02d}_*.jpg")
        archivos = sorted(glob.glob(pattern))
        if archivos:
            add_text(archivos[-1], args.video)
        else:
            print(f"No encontrado: {pattern}")
    else:
        procesar_todos()
