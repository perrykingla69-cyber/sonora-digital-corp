#!/usr/bin/env python3
"""
Generador de Videos/Shorts — HERMES
Crea videos YouTube Shorts y TikTok desde imágenes de Mystic

Uso:
  python generate_video.py --video 1 --format shorts   # YouTube Short (9:16)
  python generate_video.py --video 1 --format youtube  # YouTube normal (16:9)
  python generate_video.py --all --format shorts        # todos los shorts
  python generate_video.py --check                      # verificar dependencias
"""

import os, sys, subprocess, json, argparse, glob
from pathlib import Path
from datetime import datetime

CONTENT_DIR = Path(__file__).parent
GENERATED_DIR = CONTENT_DIR / "generated"
THUMBS_DIR = CONTENT_DIR / "thumbnails_final"
OUTPUT_DIR = CONTENT_DIR / "videos"
OUTPUT_DIR.mkdir(exist_ok=True)

# Scripts de video (resumen de puntos clave para subtítulos)
VIDEO_SCRIPTS = {
    1: {
        "titulo": "El SAT te puede multar — ¿cuánto?",
        "duracion": 30,
        "subtitulos": [
            (0, 5, "¿Sabes cuánto te puede multar el SAT?"),
            (5, 12, "Por no presentar tu DIOT a tiempo..."),
            (12, 20, "Hasta $80,000 MXN en multas."),
            (20, 28, "HERMES te avisa ANTES del vencimiento."),
            (28, 30, "sonoradigitalcorp.com"),
        ],
        "escenas": ["sat_warning", "boardroom", "ceo"],
    },
    2: {
        "titulo": "Tu contador vs HERMES",
        "duracion": 30,
        "subtitulos": [
            (0, 5, "Tu contador: $8,000/mes"),
            (5, 12, "HERMES: $799/mes"),
            (12, 20, "Disponible 24/7. Sin excusas."),
            (20, 28, "¿La diferencia? $7,201 MXN al mes."),
            (28, 30, "sonoradigitalcorp.com"),
        ],
        "escenas": ["ceo", "oracle", "whatsapp_demo"],
    },
    3: {
        "titulo": "Error MVE en aduanas — $300,000 MXN",
        "duracion": 45,
        "subtitulos": [
            (0, 6, "¿Importas mercancía a México?"),
            (6, 15, "Un error en tu MVE..."),
            (15, 25, "puede costarte $300,000 MXN en multas."),
            (25, 35, "HERMES valida tu fracción arancelaria"),
            (35, 43, "antes de que el SAT te encuentre."),
            (43, 45, "sonoradigitalcorp.com"),
        ],
        "escenas": ["boardroom", "sat_warning", "ceo"],
    },
    4: {
        "titulo": "El Día 17 — Fecha límite SAT",
        "duracion": 30,
        "subtitulos": [
            (0, 5, "El día 17 de cada mes..."),
            (5, 12, "es la fecha límite del SAT."),
            (12, 20, "¿Lo sabías? Muchos empresarios no."),
            (20, 28, "HERMES te recuerda con 5 días de anticipación."),
            (28, 30, "sonoradigitalcorp.com"),
        ],
        "escenas": ["sat_warning", "ceo", "boardroom"],
    },
    5: {
        "titulo": "Tu bot contable trabaja a las 2 AM",
        "duracion": 30,
        "subtitulos": [
            (0, 5, "Son las 2 AM..."),
            (5, 12, "Tu contador está dormido."),
            (12, 20, "HERMES está respondiendo tus preguntas."),
            (20, 28, "Disponible 24/7 por WhatsApp y Telegram."),
            (28, 30, "sonoradigitalcorp.com"),
        ],
        "escenas": ["oracle", "whatsapp_demo", "ceo"],
    },
    6: {
        "titulo": "RESICO — ¿Qué es y cuánto pagas?",
        "duracion": 45,
        "subtitulos": [
            (0, 6, "¿Estás en el RESICO?"),
            (6, 15, "El Régimen Simplificado de Confianza"),
            (15, 25, "tiene tasas desde 1% hasta 2.5%."),
            (25, 35, "Pero si no presentas a tiempo..."),
            (35, 43, "te sacan del régimen automáticamente."),
            (43, 45, "HERMES te mantiene al día."),
        ],
        "escenas": ["sat_warning", "boardroom", "oracle"],
    },
    7: {
        "titulo": "¿Cuánto te cuesta una nómina mal calculada?",
        "duracion": 30,
        "subtitulos": [
            (0, 5, "Una nómina mal timbrada..."),
            (5, 12, "puede costarte hasta $150,000 MXN."),
            (12, 20, "IMSS + SAT + multas + recargos."),
            (20, 28, "HERMES revisa cada CFDI de nómina."),
            (28, 30, "sonoradigitalcorp.com"),
        ],
        "escenas": ["boardroom", "ceo", "sat_warning"],
    },
    8: {
        "titulo": "Precio fundador — se acaba el 1 de Abril",
        "duracion": 30,
        "subtitulos": [
            (0, 5, "Precio fundador HERMES"),
            (5, 12, "Primer mes: $1,199 MXN"),
            (12, 20, "Se acaba el 1 de Abril."),
            (20, 28, "Después sube. No dije que no te avisé."),
            (28, 30, "sonoradigitalcorp.com"),
        ],
        "escenas": ["oracle", "ceo", "rooftop"],
    },
    9: {
        "titulo": "CFDI 4.0 — El error que más multas genera",
        "duracion": 45,
        "subtitulos": [
            (0, 6, "CFDI 4.0 entró en vigor en 2023."),
            (6, 15, "El error más común: RFC receptor incorrecto."),
            (15, 25, "El SAT puede rechazar tu factura completa."),
            (25, 35, "HERMES valida cada campo antes de timbrar."),
            (35, 43, "Cero errores. Cero multas."),
            (43, 45, "sonoradigitalcorp.com"),
        ],
        "escenas": ["sat_warning", "oracle", "boardroom"],
    },
    10: {
        "titulo": "Cierre mensual en 10 minutos",
        "duracion": 30,
        "subtitulos": [
            (0, 5, "¿Cuánto tiempo te toma cerrar el mes?"),
            (5, 12, "¿3 días? ¿Una semana?"),
            (12, 20, "Con HERMES: 10 minutos."),
            (20, 28, "Conciliación automática. Reportes instantáneos."),
            (28, 30, "sonoradigitalcorp.com"),
        ],
        "escenas": ["ceo", "blockchain", "oracle"],
    },
}

# Dimensiones por formato
FORMATOS = {
    "shorts": {"w": 1080, "h": 1920, "label": "9:16"},
    "youtube": {"w": 1920, "h": 1080, "label": "16:9"},
    "tiktok": {"w": 1080, "h": 1920, "label": "9:16"},
}

def check_ffmpeg():
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_scene_image(scene_name: str) -> str | None:
    """Busca la imagen más reciente de una escena."""
    pattern = str(GENERATED_DIR / f"{scene_name}_*.jpg")
    files = sorted(glob.glob(pattern))
    return files[-1] if files else None

def find_font() -> str:
    """Busca una fuente disponible en el sistema."""
    candidates = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        "/System/Library/Fonts/Helvetica.ttc",  # macOS fallback
    ]
    for f in candidates:
        if os.path.exists(f):
            return f
    # Intento genérico
    result = subprocess.run(
        ["fc-match", "-f", "%{file}", "sans-serif:bold"],
        capture_output=True, text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return candidates[0]  # fallback aunque no exista (ffmpeg intentará)

def create_video(video_num: int, formato: str = "shorts") -> str | None:
    """Crea un video para el formato indicado."""
    if not check_ffmpeg():
        print("ERROR: ffmpeg no instalado. Ejecuta: sudo apt-get install ffmpeg -y")
        return None

    script = VIDEO_SCRIPTS.get(video_num)
    if not script:
        print(f"Video #{video_num} no tiene script definido")
        return None

    fmt = FORMATOS.get(formato, FORMATOS["shorts"])
    w, h = fmt["w"], fmt["h"]

    print(f"\nCreando {formato.upper()} #{video_num}: {script['titulo']}")
    print(f"  Dimensiones: {w}x{h} ({fmt['label']})")

    # Obtener imágenes disponibles
    imagenes = []
    for escena in script["escenas"]:
        img = get_scene_image(escena)
        if img:
            imagenes.append(img)
            print(f"  Escena '{escena}': {Path(img).name}")
        else:
            print(f"  AVISO: Escena '{escena}' sin imagen, se omite")

    if not imagenes:
        print(f"  ERROR: No hay imágenes generadas.")
        print(f"  Ejecuta: python generate_content.py --batch")
        return None

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"{formato}_v{video_num:02d}_{ts}.mp4"

    duracion_total = script["duracion"]
    duracion_por_img = duracion_total / len(imagenes)
    fps = 25

    font_path = find_font()
    font_size = 52 if formato in ("shorts", "tiktok") else 46

    # Construir inputs y filtros
    inputs_args = []
    filter_parts = []

    for i, img_path in enumerate(imagenes):
        inputs_args += ["-loop", "1", "-t", str(duracion_por_img), "-i", img_path]

        d_frames = int(duracion_por_img * fps)
        zoom_end = 1.0 + 0.04 + (i * 0.02)
        zoom_end = min(zoom_end, 1.10)  # cap al 110%

        filter_parts.append(
            f"[{i}:v]"
            f"scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},"
            f"zoompan="
            f"z='min(zoom+0.0015,{zoom_end:.3f})':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={d_frames}:fps={fps}:s={w}x{h}"
            f"[v{i}]"
        )

    # Concatenar todos los clips
    concat_inputs = "".join(f"[v{i}]" for i in range(len(imagenes)))
    filter_parts.append(
        f"{concat_inputs}concat=n={len(imagenes)}:v=1:a=0[vconcat]"
    )

    # Subtítulos con drawtext
    sub_filter = "[vconcat]"
    for idx, (start, end, texto) in enumerate(script["subtitulos"]):
        # Escapar caracteres especiales para ffmpeg drawtext
        texto_esc = (texto
            .replace("\\", "\\\\")
            .replace("'", "\u2019")   # comilla tipográfica para evitar conflicto
            .replace(":", "\\:")
            .replace(",", "\\,")
            .replace("[", "\\[")
            .replace("]", "\\]")
        )
        output_label = f"[vsub{idx}]" if idx < len(script["subtitulos"]) - 1 else "[vfinal]"
        # Fondo semitransparente usando box
        sub_filter += (
            f"drawtext="
            f"fontfile={font_path}:"
            f"text='{texto_esc}':"
            f"fontsize={font_size}:"
            f"fontcolor=white:"
            f"bordercolor=black:"
            f"borderw=3:"
            f"box=1:"
            f"boxcolor=black@0.45:"
            f"boxborderw=8:"
            f"x=(w-text_w)/2:"
            f"y=h-220:"
            f"enable='between(t,{start},{end})'"
            f"{output_label}"
        )
        if idx < len(script["subtitulos"]) - 1:
            sub_filter = f"{output_label}"

    # Reconstruir la cadena de subtítulos correctamente
    sub_filters = []
    for idx, (start, end, texto) in enumerate(script["subtitulos"]):
        texto_esc = (texto
            .replace("\\", "\\\\")
            .replace("'", "\u2019")
            .replace(":", "\\:")
            .replace(",", "\\,")
            .replace("[", "\\[")
            .replace("]", "\\]")
        )
        sub_filters.append(
            f"drawtext="
            f"fontfile={font_path}:"
            f"text='{texto_esc}':"
            f"fontsize={font_size}:"
            f"fontcolor=white:"
            f"bordercolor=black:"
            f"borderw=3:"
            f"box=1:"
            f"boxcolor=black@0.45:"
            f"boxborderw=8:"
            f"x=(w-text_w)/2:"
            f"y=h-220:"
            f"enable='between(t,{start},{end})'"
        )

    # Encadenar todos los drawtext como un solo filtro sobre vconcat
    full_sub = "[vconcat]" + ",".join(sub_filters) + "[vfinal]"
    filter_parts.append(full_sub)

    filter_complex = ";".join(filter_parts)

    cmd = (
        inputs_args +
        [
            "-filter_complex", filter_complex,
            "-map", "[vfinal]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-r", str(fps),
            "-pix_fmt", "yuv420p",
            "-t", str(duracion_total),
            "-movflags", "+faststart",
            "-y", str(output_path)
        ]
    )

    print(f"  Procesando {len(imagenes)} escenas × {duracion_por_img:.1f}s = {duracion_total}s total...")
    try:
        result = subprocess.run(
            ["ffmpeg", "-loglevel", "warning"] + cmd,
            capture_output=True, text=True, timeout=180
        )
        if result.returncode == 0:
            if output_path.exists():
                size = output_path.stat().st_size / 1024 / 1024
                print(f"  OK: {output_path.name} ({size:.1f} MB)")
                return str(output_path)
            else:
                print(f"  ERROR: El archivo no fue creado.")
                if result.stderr:
                    print(f"  stderr: {result.stderr[-800:]}")
                return None
        else:
            print(f"  ERROR ffmpeg (código {result.returncode}):")
            print(f"  {result.stderr[-800:]}")
            return None
    except subprocess.TimeoutExpired:
        print("  ERROR: Timeout (>180s) — video muy largo o sistema lento")
        return None

# Alias para compatibilidad con el nombre original de la función
def create_shorts(video_num: int) -> str | None:
    return create_video(video_num, "shorts")


def list_available_images():
    """Muestra las imágenes disponibles organizadas por escena."""
    imgs = sorted(GENERATED_DIR.glob("*.jpg"))
    escenas = {}
    for img in imgs:
        # Extraer nombre de escena (todo antes del timestamp)
        parts = img.stem.rsplit("_", 2)
        if len(parts) >= 2:
            escena = "_".join(parts[:-2]) if len(parts) > 2 else parts[0]
        else:
            escena = img.stem
        escenas.setdefault(escena, []).append(img.name)

    print(f"\nImagenes disponibles en {GENERATED_DIR}:")
    for escena, archivos in sorted(escenas.items()):
        print(f"  {escena}: {len(archivos)} imagen(es)")
    return escenas


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generador de Videos HERMES — Shorts, TikTok y YouTube",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python generate_video.py --check
  python generate_video.py --video 8 --format shorts
  python generate_video.py --video 1 --format youtube
  python generate_video.py --all --format shorts
        """
    )
    parser.add_argument("--video", type=int, metavar="N",
                        help="Número de video (1-10)")
    parser.add_argument("--all", action="store_true",
                        help="Generar todos los videos definidos")
    parser.add_argument("--format", choices=["shorts", "youtube", "tiktok"],
                        default="shorts",
                        help="Formato de salida (default: shorts)")
    parser.add_argument("--check", action="store_true",
                        help="Verificar dependencias y listar imágenes disponibles")
    parser.add_argument("--list-videos", action="store_true",
                        help="Listar los videos disponibles en el script")
    args = parser.parse_args()

    if args.check:
        print("=" * 50)
        print("Verificacion de dependencias — HERMES Video")
        print("=" * 50)
        ffmpeg_ok = check_ffmpeg()
        print(f"ffmpeg:  {'OK' if ffmpeg_ok else 'NO instalado (sudo apt install ffmpeg)'}")
        font = find_font()
        font_ok = os.path.exists(font)
        print(f"Fuente:  {'OK — ' + font if font_ok else 'No encontrada (se usara fallback)'}")
        list_available_images()
        thumbs = list(THUMBS_DIR.glob("*.jpg"))
        print(f"\nMiniaturas finales: {len(thumbs)}")
        print(f"Directorio output:  {OUTPUT_DIR}")
        videos_out = list(OUTPUT_DIR.glob("*.mp4"))
        print(f"Videos generados:   {len(videos_out)}")
        sys.exit(0 if ffmpeg_ok else 1)

    if args.list_videos:
        print("\nVideos disponibles:")
        for num, s in sorted(VIDEO_SCRIPTS.items()):
            escenas_str = ", ".join(s["escenas"])
            print(f"  #{num:2d} [{s['duracion']:2d}s] {s['titulo']}")
            print(f"       Escenas: {escenas_str}")
        sys.exit(0)

    if not check_ffmpeg():
        print("ERROR: ffmpeg no está instalado.")
        print("Instala con: sudo apt-get install ffmpeg -y")
        sys.exit(1)

    resultados = []

    if args.all:
        print(f"Generando TODOS los videos en formato {args.format.upper()}...")
        for num in sorted(VIDEO_SCRIPTS.keys()):
            path = create_video(num, args.format)
            resultados.append((num, path))
    elif args.video:
        path = create_video(args.video, args.format)
        resultados.append((args.video, path))
    else:
        parser.print_help()
        sys.exit(0)

    # Resumen final
    exitosos = [(n, p) for n, p in resultados if p]
    fallidos = [(n, p) for n, p in resultados if not p]

    print(f"\n{'='*50}")
    print(f"RESUMEN: {len(exitosos)}/{len(resultados)} videos generados")
    if exitosos:
        print("Videos creados:")
        for num, path in exitosos:
            size = Path(path).stat().st_size / 1024 / 1024
            print(f"  #{num}: {Path(path).name} ({size:.1f} MB)")
    if fallidos:
        print("Fallaron:")
        for num, _ in fallidos:
            print(f"  #{num}: {VIDEO_SCRIPTS[num]['titulo']}")
    print(f"Directorio: {OUTPUT_DIR}")
