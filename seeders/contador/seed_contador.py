"""
SEED QDRANT — Producto Contador
Alimenta la base de conocimiento fiscal para el primer producto de HERMES OS.

Fuentes:
- SAT: CFF, ISR, IVA, CFDI 4.0, Buzón Tributario
- DOF: Resoluciones misceláneas, modificaciones
- IMSS: Cuotas, tablas SBC
- INFONAVIT: Aportaciones, amortizaciones
- SAT Sandbox: ambiente de pruebas PAC
- Casos prácticos: declaraciones, deducciones, errores comunes
"""

import asyncio
import hashlib
import logging
import os
import sys
import httpx
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    SparseVectorParams, SparseIndexParams,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("seed.contador")

QDRANT_URL   = os.environ.get("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL   = os.environ.get("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL  = "nomic-embed-text"
CHUNK_SIZE   = 400
CHUNK_OVERLAP = 50

FUENTES_CONTADOR = [
    # ── SAT — Legislación fiscal ──────────────────────────────
    {
        "id": "sat_cff",
        "type": "url",
        "url": "https://www.sat.gob.mx/informacion_fiscal/legislacion_tributaria/paginas/Codigos_Fiscales.aspx",
        "topic": "Código Fiscal de la Federación",
        "colecciones": ["global_fiscal_mx", "global_contador"],
    },
    {
        "id": "sat_isr",
        "type": "url",
        "url": "https://www.sat.gob.mx/informacion_fiscal/legislacion_tributaria/paginas/Leyes_ISR.aspx",
        "topic": "Ley del Impuesto Sobre la Renta",
        "colecciones": ["global_fiscal_mx", "global_contador"],
    },
    {
        "id": "sat_iva",
        "type": "url",
        "url": "https://www.sat.gob.mx/informacion_fiscal/legislacion_tributaria/paginas/Leyes_IVA.aspx",
        "topic": "Ley del Impuesto al Valor Agregado",
        "colecciones": ["global_fiscal_mx", "global_contador"],
    },
    {
        "id": "sat_cfdi_guia",
        "type": "url",
        "url": "https://www.sat.gob.mx/cs/Satellite?blobcol=urldata&blobkey=id&blobtable=MungoBlobs&blobwhere=1461174568626",
        "topic": "Guía de llenado CFDI 4.0",
        "colecciones": ["global_fiscal_mx", "global_contador"],
    },
    {
        "id": "sat_facturacion",
        "type": "url",
        "url": "https://www.sat.gob.mx/consultas/operaciones/facturacion",
        "topic": "Facturación electrónica CFDI 4.0 — requisitos y procedimientos",
        "colecciones": ["global_fiscal_mx", "global_contador"],
    },
    {
        "id": "sat_buzontrib",
        "type": "url",
        "url": "https://www.sat.gob.mx/tramites/buzon-tributario",
        "topic": "Buzón Tributario — notificaciones electrónicas SAT",
        "colecciones": ["global_contador"],
    },
    {
        "id": "sat_declaraciones",
        "type": "url",
        "url": "https://www.sat.gob.mx/declaracion",
        "topic": "Declaraciones: anuales, provisionales, complementarias",
        "colecciones": ["global_fiscal_mx", "global_contador"],
    },
    {
        "id": "sat_diot",
        "type": "url",
        "url": "https://www.sat.gob.mx/tramites/25884/presenta-tu-declaracion-informativa-de-operaciones-con-terceros-(diot)",
        "topic": "DIOT — Declaración de Operaciones con Terceros",
        "colecciones": ["global_contador"],
    },
    {
        "id": "sat_rfc",
        "type": "url",
        "url": "https://www.sat.gob.mx/tramites/registro-federal-de-contribuyentes",
        "topic": "RFC — Registro Federal de Contribuyentes, alta, modificación",
        "colecciones": ["global_fiscal_mx", "global_contador"],
    },
    # ── IMSS ─────────────────────────────────────────────────
    {
        "id": "imss_cuotas",
        "type": "url",
        "url": "https://www.imss.gob.mx/patrones/cuotas-obrero-patronales",
        "topic": "Cuotas obrero-patronales IMSS 2025",
        "colecciones": ["global_contador", "global_rrhh"],
    },
    {
        "id": "imss_sbc",
        "type": "url",
        "url": "https://www.imss.gob.mx/patrones/salario-base-cotizacion",
        "topic": "Salario Base de Cotización IMSS — integración y topes",
        "colecciones": ["global_contador", "global_rrhh"],
    },
    # ── INFONAVIT ─────────────────────────────────────────────
    {
        "id": "infonavit_aportaciones",
        "type": "url",
        "url": "https://empresas.infonavit.org.mx/wps/portal/empresas/Inicio/Cumpleobligaciones/DeterminaCuotas",
        "topic": "Aportaciones INFONAVIT 5% — determinación y pago",
        "colecciones": ["global_contador", "global_rrhh"],
    },
    # ── DOF ───────────────────────────────────────────────────
    {
        "id": "dof_rss",
        "type": "rss",
        "url": "https://www.dof.gob.mx/rss.php",
        "topic": "DOF — Diario Oficial de la Federación (últimas publicaciones fiscales)",
        "colecciones": ["global_fiscal_mx", "global_contador"],
        "filter": "SAT ISR IVA CFDI miscelánea fiscal",
    },
    # ── CONOCIMIENTO INTERNO (se agrega como texto directo) ───
    {
        "id": "conocimiento_cfdi_errores",
        "type": "texto",
        "topic": "Errores comunes CFDI y cómo corregirlos",
        "colecciones": ["global_contador"],
        "contenido": """
ERRORES COMUNES EN CFDI 4.0 Y SOLUCIONES:

ERROR 1: CFDI40102 — RFC del receptor no válido
Causa: RFC del cliente no registrado o con error tipográfico
Solución: Verificar RFC en validador SAT: rfc.sat.gob.mx
Fundamento: Art. 29-A fracc. IV CFF

ERROR 2: CFDI40103 — Nombre del receptor no coincide
Causa: Nombre del cliente diferente al registrado en SAT
Solución: Solicitar Constancia de Situación Fiscal actualizada al cliente
Nota: Desde 2022 es obligatorio que nombre coincida exactamente

ERROR 3: Uso CFDI "P01 Por definir" en receptor PF
Causa: No se especificó el uso del CFDI
Solución: Solicitar al cliente el uso correcto (G03 gastos en general es el más común)
Para PF deducibles: D01 honorarios médicos, D03 gastos funerales, etc.

ERROR 4: Forma de pago "99 Por definir" en PPD
Causa: Se emitió con PPD sin especificar la forma de pago esperada
Solución: Emitir complemento de pago cuando se reciba el pago
Fundamento: Regla 2.7.1.31 RMF

ERROR 5: Moneda incorrecta o tipo de cambio faltante
Causa: Factura en USD sin capturar tipo de cambio
Solución: Siempre incluir tipo de cambio del día de la operación (DOF)
Fundamento: Art. 8 CFF

CANCELACIÓN DE CFDI:
- Desde 2022 se requiere aceptación del receptor para cancelar
- Plazo: mismo ejercicio fiscal sin restricción; años anteriores requieren aclaración
- Motivos: 01 Comprobante con errores, 02 Comprobante no relacionado con operación
- Si receptor no acepta en 3 días hábiles: cancelación automática
Fundamento: Art. 29-A CFF, Regla 2.7.1.21 RMF
""",
    },
    {
        "id": "conocimiento_sandbox_pac",
        "type": "texto",
        "topic": "SAT Sandbox — ambiente de pruebas para timbrado CFDI",
        "colecciones": ["global_contador"],
        "contenido": """
AMBIENTE DE PRUEBAS SAT (SANDBOX) PARA CFDI:

URL Sandbox SAT: https://pruebas.sat.gob.mx/timbre-fiscal/
Para pruebas de timbrado usar PACs que ofrecen ambiente de pruebas gratuito.

PACs con sandbox gratuito:
- Edicom: https://demo.edicomgroup.com
- Facturama: https://apisandbox.facturama.mx (API REST, fácil integración)
- SW Sapien: https://services.test.sw.com.mx
- CFDI SAT directamente: xml.sat.gob.mx/sitio_internet/cfd/catalogos/

Certificados de prueba SAT:
- Descargar en: https://www.sat.gob.mx/tramites/66855/genera-y-descarga-tus-archivos-a-traves-del-aplicativo-certifica
- CSD de prueba (no válidos para producción)

Validador de CFDI SAT:
- https://verificacfdi.facturaelectronica.sat.gob.mx/
- Verificar: folio fiscal (UUID), sello digital, cadena original

Flujo de timbrado:
1. Generar XML con estructura CFDI 4.0
2. Sellar con CSD del emisor
3. Enviar al PAC para timbre
4. PAC valida con SAT y devuelve UUID
5. Agregar sello SAT al XML final
6. Enviar al receptor (PDF + XML)

Human in the Loop recomendado:
- El sistema genera el CFDI
- El contador revisa montos, receptor, uso
- El contador aprueba → se timbra automáticamente
- Ante error SAT → HERMES explica la causa y propone corrección
""",
    },
    {
        "id": "conocimiento_declaracion_anual",
        "type": "texto",
        "topic": "Declaración anual personas físicas — proceso completo",
        "colecciones": ["global_contador"],
        "contenido": """
DECLARACIÓN ANUAL PERSONAS FÍSICAS — GUÍA COMPLETA:

PLAZO: Abril 30 del año siguiente al ejercicio fiscal
PLATAFORMA: portal.sat.gob.mx → Declaraciones → Declaración Anual

REGÍMENES Y SUS PARTICULARIDADES:

1. RESICO (Régimen Simplificado de Confianza):
   - Tasa del 1% al 2.5% sobre ingresos (no deducciones)
   - Pago bimestral a través de "Mis Cuentas"
   - Límite: $3.5 millones anuales
   - No aplica para actividades profesionales con honorarios > $75,000

2. Actividad Empresarial y Profesional:
   - Ingresos - Deducciones autorizadas = Utilidad fiscal
   - ISR según tabla progresiva
   - Deducciones: gastos estrictamente indispensables + deducciones personales

3. Asalariados (Sueldos y Salarios):
   - Empleador retiene ISR mensualmente
   - Declaración anual: obligatoria si ingresos > $400,000 o > 2 empleadores

DEDUCCIONES PERSONALES 2025:
- Honorarios médicos y dentales (ilimitado si tienen CFDI)
- Gastos hospitalarios (ilimitado)
- Colegiaturas: preescolar $14,200, primaria $12,900, secundaria $19,900, preparatoria $24,500
- Intereses hipotecarios reales (1 crédito)
- Aportaciones voluntarias AFORE
- Seguros de gastos médicos mayores (primas)
- Transporte escolar (obligatorio si es deducible)
TOPE: 15% del ingreso total o 5 UMAs anuales ($7,603.80 x 365 dias)

ERRORES FRECUENTES:
- No declarar todos los ingresos (SAT cruza con DIOT de terceros)
- Deducir sin CFDI a nombre del contribuyente
- No acumular intereses bancarios (aunque sean pequeños)
- Olvidar el subsidio al empleo para trabajadores con sueldo bajo
""",
    },
]


class SeedContador:
    def __init__(self):
        self.qdrant = AsyncQdrantClient(url=QDRANT_URL)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=60) as c:
            vectors = []
            for text in texts:
                r = await c.post(
                    f"{OLLAMA_URL}/api/embeddings",
                    json={"model": EMBED_MODEL, "prompt": text},
                )
                vectors.append(r.json()["embedding"])
        return vectors

    def chunk(self, text: str, source: str) -> list[dict]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
            chunk = " ".join(words[i:i + CHUNK_SIZE])
            if len(chunk.strip()) < 80:
                continue
            chunks.append({
                "text": chunk,
                "source": source,
                "idx": i // (CHUNK_SIZE - CHUNK_OVERLAP),
                "id": hashlib.md5(f"{source}:{i}".encode()).hexdigest(),
            })
        return chunks

    async def ensure_collection(self, name: str):
        cols = [c.name for c in (await self.qdrant.get_collections()).collections]
        if name not in cols:
            await self.qdrant.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                sparse_vectors_config={"bm25": SparseVectorParams(
                    index=SparseIndexParams(on_disk=False)
                )},
            )
            logger.info(f"  Colección creada: {name}")

    async def upsert(self, col: str, chunks: list[dict], meta: dict):
        await self.ensure_collection(col)
        vectors = await self.embed([c["text"] for c in chunks])
        points = []
        for chunk, vec in zip(chunks, vectors):
            points.append(PointStruct(
                id=int(hashlib.md5(chunk["id"].encode()).hexdigest(), 16) % (2**63),
                vector={"default": vec},
                payload={"text": chunk["text"], "source": chunk["source"],
                         "chunk_index": chunk["idx"], **meta},
            ))
        await self.qdrant.upsert(collection_name=col, points=points)
        logger.info(f"    ✓ {len(points)} chunks → {col}")

    async def fetch(self, fuente: dict) -> str:
        if fuente["type"] == "texto":
            return fuente.get("contenido", "")
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
                r = await c.get(fuente["url"])
                return r.text[:40000]
        except Exception as e:
            logger.warning(f"  No se pudo obtener {fuente['url']}: {e}")
            return ""

    async def run(self):
        logger.info("═══════════════════════════════════════")
        logger.info("  SEED QDRANT — Producto Contador")
        logger.info("═══════════════════════════════════════")

        total_chunks = 0
        for fuente in FUENTES_CONTADOR:
            logger.info(f"\n→ {fuente['topic']}")
            contenido = await self.fetch(fuente)
            if not contenido:
                logger.warning(f"  ⚠ Sin contenido — saltando")
                continue

            chunks = self.chunk(contenido, fuente.get("url", fuente["id"]))
            logger.info(f"  {len(chunks)} chunks generados")

            for col in fuente["colecciones"]:
                await self.upsert(col, chunks, {
                    "niche": "contador",
                    "topic": fuente["topic"],
                    "source_id": fuente["id"],
                    "tenant_id": "global",
                })

            total_chunks += len(chunks)

        logger.info(f"\n══════════════════════════════════════")
        logger.info(f"  ✅ Seed completado: {total_chunks} chunks totales")
        logger.info(f"  Colecciones: global_fiscal_mx, global_contador, global_rrhh")
        logger.info(f"══════════════════════════════════════")


async def main():
    seeder = SeedContador()
    await seeder.run()


if __name__ == "__main__":
    asyncio.run(main())
