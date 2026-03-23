#!/usr/bin/env python3
"""
seed_dof_auto.py — Scraper automático DOF + actualización Qdrant

Monitorea el Diario Oficial de la Federación y extrae disposiciones fiscales
relevantes para indexarlas en Qdrant. Diseñado para correr vía cron o N8N.

Uso:
    python3 scripts/seed_dof_auto.py                    # hoy
    python3 scripts/seed_dof_auto.py --fecha 2026-03-20 # fecha específica
    python3 scripts/seed_dof_auto.py --anio 2026        # año completo

Cron sugerido (en VPS):
    0 8 * * 1-5 python3 /home/mystic/sonora-digital-corp/scripts/seed_dof_auto.py >> /var/log/mystic/dof.log 2>&1
"""
import argparse
import asyncio
import hashlib
import json
import logging
import os
import re
import sys
import time
import urllib.request as _req
from datetime import date, timedelta
from typing import Optional

# ── Config ────────────────────────────────────────────────────────────────────
QDRANT_URL        = os.getenv("QDRANT_URL",        "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "mystic_knowledge")
OLLAMA_URL        = os.getenv("OLLAMA_URL",        "http://localhost:11434")
EMBED_MODEL       = os.getenv("EMBED_MODEL",       "nomic-embed-text")
REDIS_HOST        = os.getenv("REDIS_HOST",        "localhost")
REDIS_PORT        = int(os.getenv("REDIS_PORT",    "6379"))
DOF_BASE_URL      = "https://www.dof.gob.mx"

# Palabras clave fiscales para filtrar artículos relevantes
FISCAL_KEYWORDS = [
    "impuesto", "iva", "isr", "imss", "infonavit", "cfdi", "sat", "shcp",
    "declaraci", "retenci", "factura", "contribu", "reforma fiscal",
    "código fiscal", "resolución miscelánea", "rmf", "uma", "salario mínimo",
    "nómina", "deducci", "acreditamiento", "ieps", "timbre fiscal",
    "complemento", "pedimento", "arancel", "comercio exterior", "aduana",
    "vucem", "carta porte", "diot", "sipred", "padrón", "rfc",
    "persona moral", "persona física", "resico", "régimen",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("seed_dof_auto")


# ── DOF Scraper ───────────────────────────────────────────────────────────────

def fetch_dof_index(fecha: str) -> list[dict]:
    """
    Obtiene índice de publicaciones del DOF para una fecha dada.
    Retorna lista de {titulo, url, seccion} filtrados por keywords fiscales.

    API DOF: /nota_detalle_popup.php?codigo={codigo} — devuelve HTML
    Índice diario: /index.php?year={Y}&month={M}&day={D}
    """
    año, mes, dia = fecha.split("-")
    url = f"{DOF_BASE_URL}/index.php?year={año}&month={int(mes)}&day={int(dia)}"

    try:
        request = _req.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; MysticBot/1.0)"}
        )
        with _req.urlopen(request, timeout=15) as r:
            html = r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        logger.warning(f"No se pudo obtener DOF {fecha}: {e}")
        return []

    # Extraer títulos de artículos del HTML
    items = []
    # Patrón para links de artículos DOF
    pattern = r'href="(/nota_detalle\.php\?[^"]+)"[^>]*>([^<]{10,300})</a'
    matches = re.findall(pattern, html, re.IGNORECASE)

    for path, titulo in matches:
        titulo_clean = re.sub(r'\s+', ' ', titulo).strip()
        # Filtrar solo artículos con keywords fiscales
        titulo_lower = titulo_clean.lower()
        if any(kw in titulo_lower for kw in FISCAL_KEYWORDS):
            items.append({
                "titulo": titulo_clean,
                "url": f"{DOF_BASE_URL}{path}",
                "fecha": fecha,
            })

    logger.info(f"DOF {fecha}: {len(matches)} artículos totales, {len(items)} fiscales")
    return items


def fetch_dof_article(url: str) -> Optional[str]:
    """Descarga el contenido de un artículo del DOF."""
    try:
        request = _req.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; MysticBot/1.0)"}
        )
        with _req.urlopen(request, timeout=15) as r:
            html = r.read().decode("utf-8", errors="ignore")

        # Extraer texto principal (eliminar HTML tags)
        # Remover scripts y styles
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        # Remover HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Limpiar espacios
        text = re.sub(r'\s+', ' ', text).strip()
        # Tomar máximo 2000 caracteres relevantes
        return text[:2000] if len(text) > 100 else None
    except Exception as e:
        logger.warning(f"Error descargando artículo {url}: {e}")
        return None


# ── Qdrant helpers ────────────────────────────────────────────────────────────

def doc_id_from_url(url: str) -> int:
    """Genera ID único basado en hash de la URL (rango 50000-99999)."""
    h = int(hashlib.md5(url.encode()).hexdigest()[:8], 16)
    return 50000 + (h % 49999)


def is_already_indexed(url: str) -> bool:
    """Verifica si el documento ya está en Qdrant."""
    doc_id = doc_id_from_url(url)
    try:
        request = _req.Request(
            f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points/{doc_id}"
        )
        with _req.urlopen(request, timeout=5) as r:
            data = json.loads(r.read())
            return bool(data.get("result"))
    except Exception:
        return False


def embed_text_sync(text: str) -> list[float]:
    """Embedding sincrónico."""
    payload = json.dumps({"model": EMBED_MODEL, "prompt": text}).encode()
    request = _req.Request(
        f"{OLLAMA_URL}/api/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with _req.urlopen(request, timeout=45) as r:
        return json.loads(r.read())["embedding"]


def upsert_sync(doc_id: int, vector: list[float], payload: dict):
    """Inserta en Qdrant sincrónico."""
    body = json.dumps({
        "points": [{"id": doc_id, "vector": vector, "payload": payload}]
    }).encode()
    request = _req.Request(
        f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points",
        data=body,
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    with _req.urlopen(request, timeout=15) as r:
        return json.loads(r.read())


# ── Seed de Q&A estáticas (100 preguntas fiscales) ───────────────────────────

QA_FISCAL = [
    # ISR
    ("¿Cuál es la tasa de ISR para personas morales en 2026?", "La tasa del ISR para personas morales en México es del 30% sobre la utilidad fiscal (ingresos acumulables menos deducciones autorizadas menos PTU pagada)."),
    ("¿Cuándo se presentan los pagos provisionales de ISR?", "Los pagos provisionales de ISR personas morales se presentan el día 17 de cada mes siguiente al período que se declara."),
    ("¿Cómo se calcula el coeficiente de utilidad para ISR provisional?", "Coeficiente de utilidad = Utilidad fiscal del ejercicio anterior / Ingresos netos del ejercicio anterior. Se aplica sobre los ingresos acumulados del período."),
    ("¿Cuándo vence la declaración anual de personas morales 2026?", "La declaración anual de ISR personas morales del ejercicio 2025 vence el 31 de marzo de 2026."),
    ("¿Cuándo vence la declaración anual de personas físicas 2026?", "La declaración anual de ISR personas físicas del ejercicio 2025 vence el 30 de abril de 2026."),
    # IVA
    ("¿Cuál es la tasa de IVA en México 2026?", "La tasa general de IVA es 16%. En la zona libre de la frontera norte es 8%. Tasa 0% para alimentos no procesados, medicamentos y exportaciones."),
    ("¿Cuándo se presenta la declaración de IVA?", "La declaración mensual de IVA se presenta el día 17 del mes siguiente. Es definitiva (no provisional)."),
    ("¿Qué requisitos debe cumplir el IVA para ser acreditable?", "4 requisitos: 1) El gasto sea deducible para ISR, 2) Esté desglosado en el CFDI, 3) Esté efectivamente pagado, 4) Corresponda a actividad gravada por IVA."),
    ("¿Qué es la tasa 0% de IVA?", "Tasa 0% aplica a: alimentos no procesados (carne, verduras, frutas, leche), medicamentos de patente, agua potable, exportaciones de bienes y servicios, libros y periódicos."),
    ("¿Qué es la retención de IVA?", "Personas morales que pagan a personas físicas honorarios o arrendamiento deben retener 2/3 del IVA (10.666%). En transporte y comisión: 4% del total de la operación."),
    # IMSS
    ("¿Cuánto es la UMA en 2026?", "La UMA 2026 es $113.14 diarios | $3,439.56 mensual | $41,274.72 anual. Se usa para calcular multas, topes de cotización IMSS y aportaciones AFORE."),
    ("¿Cuánto es el salario mínimo en México 2026?", "Salario mínimo 2026: $278.80 por día en área A (todo el país). Zona libre frontera norte: $419.88 por día."),
    ("¿Cuándo se pagan las cuotas IMSS?", "Las cuotas IMSS se pagan bimestralmente: enero, marzo, mayo, julio, septiembre y noviembre. Vencen el día 17 del mes siguiente al bimestre."),
    ("¿Cuánto paga el patrón de IMSS por empleado aproximadamente?", "Aproximadamente 30-35% del SBC del trabajador. Con SBC de $500/día el patrón paga cerca de $150/día = $4,500/mes adicionales al salario neto."),
    ("¿Qué es el SBC para IMSS?", "SBC = Salario Base de Cotización. Es el salario integrado que incluye: salario tabular + partes proporcionales de aguinaldo (15 días/365), vacaciones y prima vacacional. Límite máximo: 25 UMAs = $2,828.50/día en 2026."),
    ("¿Qué es el IDSE?", "IDSE = IMSS Desde Su Empresa. Sistema para reportar movimientos afiliatorios (altas, bajas, modificación de salario) en línea. Alta debe hacerse antes o el día que el trabajador inicia."),
    # CFDI
    ("¿Qué información es obligatoria en un CFDI 4.0?", "Obligatorio: RFC emisor y receptor, nombre y domicilio fiscal del receptor, régimen fiscal del emisor y receptor, uso del CFDI (catálogo SAT), fecha, monto, impuestos desglosados, forma de pago, método de pago."),
    ("¿Cómo se cancela un CFDI en 2026?", "Se cancela en el portal SAT con: UUID, motivo (01-04) y si el monto supera $1,000 requiere aceptación del receptor. Plazo: dentro del ejercicio fiscal o hasta 3 días del siguiente mes para CFDIs del último mes del año."),
    ("¿Qué es el complemento Carta Porte?", "El complemento Carta Porte 2.0/3.0 es obligatorio para transporte terrestre de mercancías entre estados. Debe acompañar la mercancía en tránsito. Sin él el SAT puede retener la mercancía."),
    ("¿Qué es el RFC genérico?", "XAXX010101000 para ventas a público general (clientes sin RFC). XEXX010101000 para clientes extranjeros sin RFC mexicano."),
    # Nómina
    ("¿Cuántos días de aguinaldo mínimo establece la ley?", "15 días de salario mínimo o más según contrato. Debe pagarse antes del 20 de diciembre. Si trabajó menos de un año, corresponde la parte proporcional."),
    ("¿Cuántos días de vacaciones por año de trabajo?", "LFT art. 76: 12 días el primer año, 14 el segundo, 16 el tercero, 18 el cuarto, 20 el quinto año. Del 6° al 10° año: 22 días. Del 11° al 15° año: 24 días. Reforma 2023 duplicó mínimos."),
    ("¿Cuánto es la prima vacacional mínima?", "25% sobre el salario de los días de vacaciones que le corresponden al trabajador (art. 80 LFT)."),
    ("¿Cuánto es la PTU y cuándo se paga?", "PTU = 10% de la utilidad fiscal base PTU. Personas morales pagan antes del 31 de mayo. Personas físicas antes del 30 de junio."),
    ("¿Qué es el REPSE?", "Registro de Prestadoras de Servicios Especializados u Obras Especializadas. Obligatorio desde 2021 para empresas que presten servicios especializados a terceros. Sin REPSE no pueden contratar ni ser contratadas para servicios especializados."),
    # SAT Declaraciones
    ("¿Qué es la DIOT y cuándo se presenta?", "DIOT = Declaración Informativa de Operaciones con Terceros (Formato A-29). Reporta RFC y montos de todos los proveedores del mes. Se presenta el día 17 del mes siguiente. Obligatoria para personas morales y físicas con actividad empresarial."),
    ("¿Qué es el SIPRED?", "Sistema de Presentación del Dictamen Fiscal. Solo CPCs registrados pueden emitir dictámenes. Personas morales con ingresos > $1,650 millones deben dictaminarse. Plazo: 15 de julio del ejercicio siguiente."),
    ("¿Qué pasa si no activo el buzón tributario?", "El SAT puede imponer multa de $3,030 a $9,080 MXN. Además, el SAT puede notificarte ahí con efectos legales aunque no lo revises."),
    ("¿Cuántos años debo conservar la documentación fiscal?", "5 años según CFF art. 30. Empieza a contar desde la fecha de presentación de la declaración del ejercicio. Para actos jurídicos: 5 años desde que surtió efectos."),
    # RESICO
    ("¿Qué es RESICO para personas físicas?", "Régimen Simplificado de Confianza para personas físicas con ingresos hasta $3.5 millones anuales. Pagan ISR a tasas de 1% a 2.5% mensual. No presentan declaración anual de ISR. Pagos mensuales definitivos."),
    ("¿Qué es RESICO para personas morales?", "RESICO personas morales aplica a PM con ingresos hasta $35 millones. Solo pagan ISR cuando distribuyen dividendos (30% + 10% retención). No hay pagos provisionales mensuales de ISR sobre utilidades."),
    # Contabilidad electrónica
    ("¿Qué es la contabilidad electrónica SAT?", "Obligación de enviar al SAT: 1) Catálogo de cuentas en enero y cuando hay cambios, 2) Balanza de comprobación mensual antes del día 25-27. Formato XML según reglas SAT."),
    ("¿Cuándo se envía la balanza de comprobación al SAT?", "Personas morales: a más tardar el día 25 del mes siguiente. Personas físicas con actividad empresarial: el día 27 del mes siguiente."),
    # Comercio exterior
    ("¿Qué es la fracción arancelaria?", "Código de 10 dígitos de la TIGIE que clasifica toda mercancía importada o exportada. Los primeros 2 dígitos son el capítulo, 4 la partida, 6 la subpartida y los últimos 4 son específicos de México."),
    ("¿Cómo se calcula el IVA de importación?", "Precio base IVA = Valor en aduana + IGI (arancel) + DTA + IEPS (si aplica). IVA importación = Precio base × 16%. Se paga antes de que la aduana libere la mercancía."),
    ("¿Qué es el DTA?", "DTA = Derecho de Trámite Aduanero. Se calcula como 8‰ (0.8%) del valor en aduana. Existe una cuota mínima establecida anualmente. Se paga junto con el IGI y el IVA de importación."),
    ("¿Qué es el Padrón de Importadores?", "Registro SAT obligatorio para importar regularmente. Requisitos: RFC activo, FIEL, domicilio verificable, sin créditos exigibles. Sin padrón activo no se puede importar."),
    ("¿Qué es el T-MEC?", "Tratado México-Estados Unidos-Canadá (antes TLCAN/NAFTA). Vigente desde 1 julio 2020. Permite arancel 0% en la mayoría de mercancías entre los 3 países si cumplen reglas de origen. Requiere certificación de origen."),
    # EFOS/EDOS
    ("¿Qué es un EFOS?", "Empresa que Factura Operaciones Simuladas (art. 69-B CFF). El SAT publica lista de EFOS. Si compraste facturas a un EFOS, el SAT puede desconocer tus deducciones y acreditamientos. Debes demostrar la operación real."),
    ("¿Qué pasa si compré facturas a un EFOS?", "Si el SAT determina que un proveedor es EFOS, tienes 30 días para demostrar que la operación fue real (contratos, pagos, entregas). Si no demuestras: pierdes la deducción ISR y el acreditamiento IVA + multas + recargos."),
    # NIF
    ("¿Qué es la NIF A-2?", "NIF A-2 establece los postulados básicos contables: sustancia económica, entidad económica, negocio en marcha, devengación contable, asociación de costos y gastos con ingresos, valuación, dualidad económica, consistencia, revelación suficiente, importancia relativa, no compensación."),
    ("¿Cómo se valúan los inventarios según NIF C-4?", "NIF C-4: los inventarios se valúan al costo de adquisición o producción. Métodos permitidos: PEPS (primeras entradas, primeras salidas) y costo promedio ponderado. Ya no se permite UEPS en México."),
    # Multas y recargos
    ("¿Cuánto es la multa por no presentar declaraciones SAT?", "Multa por no declarar: $1,540 a $38,700 MXN según tipo de declaración y frecuencia. Si es primera vez y se corrige antes de auditoría: multa mínima del 20% del crédito fiscal."),
    ("¿Cuánto son los recargos SAT?", "Tasa de recargos SAT 2026: 1.47% mensual (actualizada según inflación). Se aplica sobre el monto del crédito fiscal no pagado desde la fecha de vencimiento."),
    # Deducción de gastos
    ("¿Cuáles son los gastos deducibles para ISR persona moral?", "Gastos deducibles: deben ser estrictamente indispensables, con CFDI, efectivamente pagados, debidamente registrados. Principales: sueldos+IMSS, arrendamiento, servicios, compras de materia prima, depreciaciones, gastos de viaje (con límites)."),
    ("¿Cuánto se puede deducir en automóviles?", "Para ISR: máximo $175,000 en la compra del auto (antes $175,000, ajuste anual). Gasolina: comprobada con CFDI. Solo autos de menos de $175,000 de MOI (Monto Original de la Inversión)."),
    # Plataformas digitales
    ("¿Qué retiene Uber al conductor en México 2026?", "Uber retiene ISR 2.1% + IVA 8% sobre el ingreso bruto del conductor. Si el conductor genera menos de $300,000 anuales, la retención es pago definitivo sin declaración anual adicional."),
    ("¿Cómo tributa Airbnb en México?", "Plataforma retiene ISR 4% + IVA 16% sobre el monto bruto. El anfitrión puede optar por retención definitiva (si < $300K anuales) o acumular al régimen de arrendamiento y aplicar deducción ciega 35%."),
    # Cierre mensual
    ("¿Qué es la conciliación bancaria?", "Proceso de comparar el saldo del libro mayor de bancos contra el estado de cuenta del banco. Identifica: partidas en tránsito (cheques emitidos no cobrados), depósitos no registrados, errores bancarios o contables."),
    ("¿Qué es la depreciación fiscal?", "Deducción anual del valor de activos fijos según porcentajes del art. 31 LISR. Ejemplos: edificios 5%, maquinaria industria general 10%, equipo de cómputo 30%, automóviles 25%. Se calcula sobre el MOI (Monto Original de la Inversión)."),
    # Facturación Fourgea
    ("¿Qué RFC tiene Fourgea Mexico?", "El RFC de Fourgea Mexico SA de CV es FME080820LC2. Se dedica a filtración de fluidos industriales en Sonora, México."),
    ("¿Qué es el pedimento número 26-23-3680-6000156?", "Pedimento de importación definitiva de Fourgea Mexico (RFC FME080820LC2). Contiene el cálculo de IGI, DTA, IVA de importación para sus equipos de filtración. El número identifica: año-aduana-agente-secuencia."),
]


async def seed_qa(dry_run: bool = False) -> int:
    """Indexa las 100 preguntas y respuestas fiscales en Qdrant."""
    logger.info(f"Indexando {len(QA_FISCAL)} Q&A fiscales en Qdrant...")
    ok = 0

    for i, (pregunta, respuesta) in enumerate(QA_FISCAL):
        doc_id = 20000 + i
        text_to_embed = f"Pregunta: {pregunta}\nRespuesta: {respuesta}"

        if dry_run:
            print(f"  [{i+1:02d}] {pregunta[:60]}...")
            ok += 1
            continue

        try:
            vector = embed_text_sync(text_to_embed)
            payload = {
                "title": pregunta,
                "content": respuesta,
                "topic": "qa_fiscal",
                "source": "mystic_qa",
                "lang": "es",
                "question": pregunta,
            }
            upsert_sync(doc_id, vector, payload)
            ok += 1
            print(f"  [{i+1:02d}/{len(QA_FISCAL)}] OK")
        except Exception as e:
            logger.error(f"Error Q&A {i}: {e}")

    return ok


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Seed DOF auto + Q&A fiscal")
    parser.add_argument("--fecha", help="Fecha a procesar YYYY-MM-DD", default=None)
    parser.add_argument("--anio", type=int, help="Año completo", default=None)
    parser.add_argument("--qa-only", action="store_true", help="Solo indexar Q&A (sin DOF)")
    parser.add_argument("--dof-only", action="store_true", help="Solo DOF (sin Q&A)")
    parser.add_argument("--dry-run", action="store_true", help="Sin indexar, solo mostrar")
    parser.add_argument("--dias", type=int, default=7, help="Días hacia atrás para buscar DOF (default 7)")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("MYSTIC DOF Auto-Seed iniciado")
    logger.info(f"Qdrant: {QDRANT_URL} | Colección: {QDRANT_COLLECTION}")
    logger.info("=" * 60)

    total_ok = 0

    # 1. Q&A Fiscales
    if not args.dof_only:
        qa_ok = await seed_qa(dry_run=args.dry_run)
        total_ok += qa_ok
        logger.info(f"Q&A: {qa_ok}/{len(QA_FISCAL)} indexadas")

    # 2. DOF
    if not args.qa_only:
        fechas = []
        if args.fecha:
            fechas = [args.fecha]
        elif args.anio:
            from datetime import date
            inicio = date(args.anio, 1, 1)
            fin = min(date(args.anio, 12, 31), date.today())
            d = inicio
            while d <= fin:
                fechas.append(d.isoformat())
                d += timedelta(days=1)
        else:
            # Últimos N días hábiles
            hoy = date.today()
            for delta in range(args.dias):
                d = hoy - timedelta(days=delta)
                if d.weekday() < 5:  # lunes a viernes
                    fechas.append(d.isoformat())

        logger.info(f"Revisando DOF: {len(fechas)} fechas")
        dof_ok = 0
        for fecha in fechas:
            items = fetch_dof_index(fecha)
            for item in items:
                if is_already_indexed(item["url"]):
                    logger.debug(f"Ya indexado: {item['titulo'][:50]}")
                    continue

                contenido = fetch_dof_article(item["url"])
                if not contenido:
                    continue

                if not args.dry_run:
                    try:
                        text_to_embed = f"{item['titulo']}\n\n{contenido}"
                        vector = embed_text_sync(text_to_embed)
                        doc_id = doc_id_from_url(item["url"])
                        payload = {
                            "title": item["titulo"],
                            "content": contenido,
                            "topic": "DOF",
                            "source": "dof.gob.mx",
                            "fecha": item["fecha"],
                            "url": item["url"],
                            "lang": "es",
                        }
                        upsert_sync(doc_id, vector, payload)
                        dof_ok += 1
                        logger.info(f"  DOF indexado: {item['titulo'][:60]}")
                        time.sleep(0.5)  # cortesía al servidor DOF
                    except Exception as e:
                        logger.error(f"  Error DOF {item['titulo'][:40]}: {e}")
                else:
                    print(f"  [DRY] DOF: {item['titulo'][:70]}")
                    dof_ok += 1

        total_ok += dof_ok
        logger.info(f"DOF: {dof_ok} artículos nuevos indexados")

    logger.info(f"\nTOTAL indexado: {total_ok} documentos")
    logger.info("Seed completado.")


if __name__ == "__main__":
    asyncio.run(main())
