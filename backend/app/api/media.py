"""
media.py — Endpoints de OCR (imagen → texto) y Whisper (audio → texto)
POST /api/media/ocr    — recibe imagen, devuelve texto extraído + datos fiscales
POST /api/media/stt    — recibe audio, devuelve transcripción
POST /api/media/factura-foto — recibe imagen de recibo, devuelve borrador de factura
"""
import io
import tempfile
import os
import re
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/media", tags=["media"])

# Whisper carga lazy — solo cuando se necesita (evitar OOM al iniciar)
_whisper_model = None

def get_whisper():
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            logger.info("Cargando modelo Whisper 'small'...")
            _whisper_model = whisper.load_model("small")
            logger.info("Whisper listo")
        except Exception as e:
            raise HTTPException(503, f"Whisper no disponible: {e}")
    return _whisper_model


def extraer_datos_fiscales(texto: str) -> dict:
    """Extrae RFC, monto, concepto del texto OCR usando regex."""
    rfc_pattern = r'[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}'
    monto_pattern = r'\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'

    rfcs = re.findall(rfc_pattern, texto.upper())
    montos = re.findall(monto_pattern, texto)

    # Monto mayor como total probable
    total = 0.0
    for m in montos:
        try:
            val = float(m.replace(',', ''))
            if val > total:
                total = val
        except ValueError:
            pass

    return {
        "rfcs_detectados": list(set(rfcs)),
        "rfc_emisor": rfcs[0] if rfcs else None,
        "total_detectado": total if total > 0 else None,
        "texto_completo": texto.strip(),
    }


# ── OCR — imagen → texto ─────────────────────────────────────────────
@router.post("/ocr")
async def ocr_imagen(file: UploadFile = File(...)):
    """
    Recibe imagen (jpg/png/webp) y extrae el texto con Tesseract.
    Retorna texto + datos fiscales detectados (RFC, monto).
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Solo se aceptan imágenes (jpg, png, webp)")

    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))

        # OCR en español + inglés para números
        texto = pytesseract.image_to_string(img, lang="spa+eng", config="--psm 6")
        datos = extraer_datos_fiscales(texto)

        return {
            "ok": True,
            "texto": datos["texto_completo"],
            "rfc_emisor": datos["rfc_emisor"],
            "rfcs": datos["rfcs_detectados"],
            "total": datos["total_detectado"],
        }
    except Exception as e:
        logger.error(f"Error OCR: {e}")
        raise HTTPException(500, f"Error procesando imagen: {e}")


# ── STT — audio → texto (Whisper) ───────────────────────────────────
@router.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    """
    Recibe audio (ogg/mp3/wav/m4a) y transcribe con Whisper small.
    Detecta español automáticamente.
    """
    allowed = {"audio/ogg", "audio/mpeg", "audio/wav", "audio/x-wav",
               "audio/mp4", "audio/m4a", "audio/webm", "application/octet-stream"}

    try:
        model = get_whisper()
        contents = await file.read()

        # Guardar temp y transcribir
        suffix = os.path.splitext(file.filename or "audio.ogg")[1] or ".ogg"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        try:
            result = model.transcribe(tmp_path, language="es", task="transcribe")
            texto = result["text"].strip()
        finally:
            os.unlink(tmp_path)

        return {
            "ok": True,
            "texto": texto,
            "idioma": "es",
            "duracion_seg": round(result.get("duration", 0), 1),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error STT: {e}")
        raise HTTPException(500, f"Error transcribiendo audio: {e}")


# ── FOTO → BORRADOR DE FACTURA ───────────────────────────────────────
@router.post("/factura-foto")
async def factura_desde_foto(file: UploadFile = File(...)):
    """
    Pipeline completo: foto de recibo → extracción OCR → borrador CFDI.
    El usuario confirma y se genera la factura real.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Solo se aceptan imágenes")

    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))
        texto = pytesseract.image_to_string(img, lang="spa+eng", config="--psm 6")
        datos = extraer_datos_fiscales(texto)

        # Construir borrador legible para el usuario
        borrador = {
            "confirmacion_requerida": True,
            "datos_detectados": {
                "rfc_emisor": datos["rfc_emisor"] or "No detectado",
                "total": datos["total_detectado"],
                "texto_original": datos["texto_completo"][:300],
            },
            "mensaje": _generar_mensaje_confirmacion(datos),
            "siguiente_paso": "Confirma los datos o corrígelos para generar el CFDI"
        }

        return {"ok": True, "borrador": borrador}
    except Exception as e:
        logger.error(f"Error factura-foto: {e}")
        raise HTTPException(500, f"Error procesando imagen: {e}")


def _generar_mensaje_confirmacion(datos: dict) -> str:
    rfc = datos.get("rfc_emisor") or "RFC no detectado"
    total = datos.get("total_detectado")
    monto_str = f"${total:,.2f} MXN" if total else "monto no detectado"
    return (
        f"Detecté un recibo de {rfc} por {monto_str}. "
        "¿Quieres que genere la factura con estos datos, o necesitas corregir algo?"
    )
