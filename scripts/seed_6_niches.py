#!/usr/bin/env python3
"""
SEED 6 NICHOS EN QDRANT — Script stand-alone para VPS
Seed automático: restaurante, contador, pastelero, abogado, constructor (fontanero), general (consultor)

Uso:
  python3 /home/mystic/hermes-os/scripts/seed_6_niches.py

Conecta a:
  - Qdrant: localhost:6333
  - Ollama: localhost:11434 (nomic-embed-text, 768-dim)

Retorna:
  - 6 nichos seeded
  - Cantidad de vectores por colección
"""

import asyncio
import httpx
import hashlib
import logging
import os
import sys
from datetime import datetime
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    SparseVectorParams, SparseIndexParams,
)

# ── LOGGING ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ── CONFIG ───────────────────────────────────────────────
QDRANT_URL = "http://localhost:6333"
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", "hermes-qdrant-internal")
OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Nichos a seed (mapeado a niche_registry.py)
NICHOS_A_SEED = [
    "restaurante",
    "contador",
    "pastelero",
    "abogado",
    "constructor",  # fontanero
    "general",      # consultor
]

# Fuentes dummy (para MVP — en producción fetch real desde URLs)
DUMMY_SOURCES = {
    "restaurante": [
        {
            "source": "NOM-251-SSA1-2009",
            "text": "Buenas Prácticas de Manufactura en Restaurantes. La preparación de alimentos debe cumplir con normas de higiene: lavado de manos cada 20 minutos, mantenimiento de cadena de frío a 4°C, separación de crudos y cocidos, capacitación en HACCP, inspecciones sanitarias mensuales. Los menús deben identificar alérgenos: gluten, cacahuate, mariscos, lácteos. Trazabilidad: origen de ingredientes, proveedores autorizados por COFEPRIS. Registros obligatorios: proveedores, recepción, almacenamiento, preparación. Uniforme: color claro, redecilla, tapa bocas. Instalaciones: drenaje, agua potable, ventilación, iluminación mínima 500 lux. Responsable Sanitario acreditado. Auditorías internas trimestrales."
        },
        {
            "source": "SAT-Restaurante-2026",
            "text": "Obligaciones fiscales: Registro ante SAT con actividad 6321 (restaurantes, cafeterías). RFC obligatorio. Emisión de CFDI con serie autogenerada (formato máximo 16 caracteres). Timbre Digital Obligatorio: cada factura requiere expedición vía CFDI 4.0. Retención de IVA en comidas (tasa 16%). Tenencia de comprobantes de proveedores: fotocopia RFC, CURP de responsable sanitario. Deducción: gas, agua, ingredientes, servicios. No deducible: caja chica > $2500, gastos personales. Libro de ingresos y egresos. Pagos estimados mensuales o declaración anual. Inspección PRODECON cada 2 años. Multas por falta de CFDI: $1000-$5000 por comprobante."
        }
    ],
    "contador": [
        {
            "source": "CFF-2026",
            "text": "Código Fiscal Federal 2026. Derechos y obligaciones de contribuyentes. ISR (Impuesto Sobre la Renta): tasa progresiva 1.92%-35% según ingresos. Base: ingresos - deducciones autorizadas. Deducibles: sueldos, renta, servicios, depreciación (línea recta). No deducibles: multas, sanciones, ISR propio. Declaración anual: 31 de marzo siguiente al ejercicio. Pagos mensuales: 16 o 17 del mes siguiente. IVA (Impuesto al Valor Agregado): tasa general 16%, tasa reducida fronteriza 8%. Acreditamiento: IVA pagado en compras puede restarse. Régimen de Personas Morales: sociedades mercantiles, asociaciones civiles. Régimen Personas Físicas: autónomos, profesionistas, comerciantes. CFDI: obligatorio desde 2010, versión 4.0 desde 2022. Retenciones: proveedores de servicios (10% ISR, 16% IVA)."
        },
        {
            "source": "CFDI-2026",
            "text": "Facturación electrónica CFDI 4.0. Expedición: mediante PAC (Proveedor Autorizado de Certificación) o directamente en SAT. Requisitos: RFC certificado, contraseña homoclave, sellos digitales válidos. Estructura: emisor, receptor, conceptos, totales, complementos. Complemento de Pago: obligatorio si no se paga en acto único (para crédito). Folio: secuencia correlativa por serie, máximo 20 dígitos. Fecha emisión: máximo 3 días. Descuentos: se registran en conceptos con tipo 'descuento', con UUID ligado. Clave de Producto/Servicio: catálogo SAT (CCP), ejemplo: 01010000 (siembra de maíz). Comprobante de recepción: receptor recibe XML y ACK. Cancelación: mediante solicitud en SAT Portal, si no se pagó. Auditoría: SAT revisa muestras aleatorias. Penalidad por incumplimiento: recargos 50-300% del impuesto."
        }
    ],
    "pastelero": [
        {
            "source": "NOM-086-SSA1-1994",
            "text": "Etiquetado de productos de repostería. Contenedor: características físicas (peso, volumen), marca comercial, datos responsable, ingredientes en orden descendente por peso. Alérgenos: frases claras: 'Contiene: gluten, huevo, leche, cacahuate, trazas de...'. Información nutricional obligatoria: calorías, grasas totales (incluido saturado y trans), colesterol, sodio, carbohidratos (incluido fibra y azúcares), proteínas, porcentaje de Valor Diario. Ingredientes a declarar: colorantes artificiales ('puede afectar actividad y atención en niños'), conservadores, edulcorantes. Fecha de elaboración, vencimiento (máximo 30 días si sin conservadores, 90 si conservados). Instrucciones almacenamiento: temperatura, humedad. Origen: 'Hecho en México', datos fabricante. Presentación: letra mínima 6pt (excepto panaderías artesanales pequeñas con exención SAT)."
        },
        {
            "source": "Costos-Pasteleria",
            "text": "Análisis de costos en repostería. Margen típico: 40-50% sobre costo de materia prima. Ingredientes principales: harina ($15/kg), azúcar ($20/kg), huevo ($0.50c/pieza), mantequilla ($80/kg), levadura ($30/paquete), chocolate ($120/kg). Fruta fresca (fresas, arándanos): $40-60/kg según estación. Producción por lote: 12-15 pasteles medianos = $180-250 costo total. PVU recomendado: $25-35 por pastel. Mano de obra: panadero $15,000/mes (puede hacer 400 pasteles/mes = $37.50/unidad labor). Alquiler local pequeño ($500-1000/mes distribuido en ~1000 unidades = $0.50-1/unidad). Empaques (caja, papel): $2-3/unidad. Rentabilidad: 35-45% tras todos costos."
        }
    ],
    "abogado": [
        {
            "source": "Codigo-Civil-MX",
            "text": "Código Civil Federal. Personas Físicas: capacidad jurídica completa a los 18 años. Domicilio: lugar donde residen habitualmente. Contrato: acuerdo de voluntades para crear obligaciones. Elementos: consentimiento (oferta + aceptación), objeto lícito, causa lícita. Vicios: error, dolo, violencia, lesión (desproporción > 50% en contraprestación). Responsabilidad: culpa o dolo. Daño: lesión a bien jurídico (patrimonio, honor, integridad). Acción: derecho a ejercer pretensión ante tribunal. Prescripción: 4 años ordinario, 10 años para inmuebles. Propiedad: derecho exclusivo a usar, gozar, disponer cosa. Posesión: tenencia de hecho. Servidumbre: gravamen inmueble en favor de otro. Herencia: sucesión de bienes tras muerte. Testamento: documento donde testador dispone patrimonio."
        },
        {
            "source": "Mercantil-Competencia",
            "text": "Ley de Competencia Económica. Prohibidas: prácticas monopólicas, acuerdos colusorios, abuso posición dominante. Monitoreo: COFECE (Comisión Federal Competencia Económica). Sanciones: multas hasta 10% ingresos anuales, comiso bienes ilícitos, cancelación concesiones. Defensa: recurso de revisión ante TFJA (Tribunal Federal). Conductas prohibidas: fijar precios, limitar producción, repartir mercados, boicot, negativa injustificada venta, depredación precios. Empresas grandes (> 50 trabajadores o ingresos > $250M anuales): obligación reportar concentraciones económicas."
        }
    ],
    "constructor": [
        {
            "source": "NOM-001-STPS-2021",
            "text": "Norma construcción. Seguridad en obra: andamios con carga máxima indicada, escaleras con baranda, arnés caída > 1.8m, casco obligatorio, guantes, protectores auditivos (> 85 dB). Inspector: supervisor acreditado debe estar presente. Riesgos: caídas, objetos punzantes, derrumbes, corrosión, trabajo en altura. Plan de seguridad: debe estar visible en acceso principal. Primeros auxilios: botiquín y personal capacitado. Jornada: máximo 8 horas, descanso dominical. Permisos: licencia municipal construcción, permisos ambientales, permisos agua/electricidad. Responsabilidad civil: constructor responde por defectos 5 años (LGAC)."
        },
        {
            "source": "Contrato-Construccion",
            "text": "Estructura contrato obra. Partes: propietario y constructor. Objeto: descripción bien inmueble, planos, especificaciones. Plazo: cronograma de ejecución. Valor: precio total o por unidad obra (metro cuadrado, lineal). Pago: anticipo (máx 5%), avances mensuales (90% a término), retención garantía (5-10%, 1 año). Obligaciones constructor: entregar conforme proyecto, calidad materiales, cumplir plazos, mantener orden. Obligaciones propietario: pagar puntualmente, proporcionar acceso. Garantía: 5 años vicios aparentes, 10 años estructurales (LGAC). Incumplimiento: penalización 1-2% por mes retraso. Resolución: puede propietario rescindir si > 30 días atraso, con retención pago proporcionado."
        }
    ],
    "general": [
        {
            "source": "SAT-General-2026",
            "text": "SAT Servicio de Administración Tributaria. Misión: recaudar impuestos federales, administrar aduanas, combatir fraude. Impuestos administrados: ISR, IVA, IEPS, tenencia, importación-exportación. Trámites: RFC, inscripción, declaraciones, pagos. Servicios: buzón tributario (notificaciones digitales), citas, asesoría telefónica. Portal: sat.gob.mx, acceso con RFC + contraseña homoclave. Sanciones: multas 50-300% dependiendo falta, comiso bienes, cancelación RFC, antecedentes penales si defraudación. Resoluciones: recurso de revocación (30 días) o amparo ante TFJA (60 días)."
        },
        {
            "source": "Empresa-Pyme-2026",
            "text": "Definición PYME en México. Pequeña empresa: 11-50 trabajadores, ingresos $2.5M-$25M anuales. Mediana: 51-250 trabajadores, ingresos $25M-$250M anuales. Microempresa: 1-10 trabajadores, ingresos < $2.5M. Incentivos: FIRA (financiamiento agrario), INADEM (créditos desarrollo), exenciones tributarias transitorias. Obligaciones contables: Libro Mayor, inventarios anuales, comprobantes fiscales. Registro: RUES, RFC, licencia municipal, registro mercantil. Cumplimiento laboral: afiliar IMSS, pagar reparto utilidades (10% utilidad anual), contrato individual. Responsabilidad: limitada si constitución oportuna, solidaria si sin formalizar."
        }
    ]
}


# ── SEEDER CLASS ─────────────────────────────────────────
class Seeder6Niches:
    def __init__(self):
        self.qdrant = AsyncQdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        self.stats = {}

    async def health_check(self):
        """Verifica que Qdrant y Ollama estén disponibles."""
        try:
            collections = await self.qdrant.get_collections()
            logger.info(f"✅ Qdrant OK — {len(collections.collections)} colecciones existentes")
        except Exception as e:
            logger.error(f"❌ Qdrant no disponible: {e}")
            sys.exit(1)

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(f"{OLLAMA_URL}/api/tags")
                models = r.json().get("models", [])
                if any(m["name"].startswith(EMBED_MODEL) for m in models):
                    logger.info(f"✅ Ollama OK — modelo {EMBED_MODEL} disponible")
                else:
                    logger.warning(f"⚠️  Ollama: {EMBED_MODEL} NO encontrado, usando fallback dummy")
        except Exception as e:
            logger.error(f"❌ Ollama no disponible: {e}")
            logger.warning("⚠️  Usando embeddings dummy para demo")

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Genera vectores densos con nomic-embed-text (Ollama)."""
        vectors = []
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                for text in texts:
                    r = await client.post(
                        f"{OLLAMA_URL}/api/embeddings",
                        json={"model": EMBED_MODEL, "prompt": text},
                    )
                    if r.status_code == 200:
                        vectors.append(r.json()["embedding"])
                    else:
                        # Fallback: vector dummy (768 dimensiones)
                        vectors.append([0.1 * (i % 768) for i in range(768)])
        except Exception as e:
            logger.warning(f"⚠️  Embed fallback (Ollama error: {e})")
            vectors = [[0.1 * (i % 768) for i in range(768)] for _ in texts]
        return vectors

    def chunk_text(self, text: str, source: str) -> list[dict]:
        """Divide texto en chunks de 500 palabras con 50% overlap."""
        words = text.split()
        chunks = []
        step = CHUNK_SIZE - CHUNK_OVERLAP
        for i in range(0, len(words), step):
            chunk = " ".join(words[i : i + CHUNK_SIZE])
            if len(chunk.strip()) < 50:
                continue
            chunks.append({
                "text": chunk,
                "source": source,
                "chunk_index": i // step,
                "id": hashlib.md5(f"{source}:{i}".encode()).hexdigest(),
            })
        return chunks

    async def ensure_collection(self, name: str):
        """Crea colección si no existe."""
        try:
            collections = await self.qdrant.get_collections()
            existing = [c.name for c in collections.collections]
            if name not in existing:
                await self.qdrant.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                    sparse_vectors_config={
                        "bm25": SparseVectorParams(
                            index=SparseIndexParams(on_disk=False)
                        )
                    },
                )
                logger.info(f"  → Colección creada: {name}")
            else:
                logger.info(f"  → Colección existente: {name}")
        except Exception as e:
            logger.error(f"❌ Error creando colección {name}: {e}")

    async def upsert_chunks(self, collection: str, chunks: list[dict], niche: str):
        """Upsert chunks a Qdrant."""
        if not chunks:
            return 0

        try:
            await self.ensure_collection(collection)
            texts = [c["text"] for c in chunks]
            vectors = await self.embed(texts)

            points = []
            for chunk, vector in zip(chunks, vectors):
                point_id = int(hashlib.md5(chunk["id"].encode()).hexdigest(), 16) % (2**63)
                points.append(PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "text": chunk["text"],
                        "source": chunk["source"],
                        "chunk_index": chunk["chunk_index"],
                        "niche": niche,
                        "tenant_id": "global",
                    },
                ))

            await self.qdrant.upsert(collection_name=collection, points=points)
            logger.info(f"  ✓ {len(points)} chunks → {collection}")
            return len(points)
        except Exception as e:
            logger.error(f"❌ Error upsert {collection}: {e}")
            return 0

    async def seed_niche(self, niche: str, sources: list[dict]):
        """Seed un nicho completo."""
        logger.info(f"\n🌱 SEED: {niche.upper()}")
        self.stats[niche] = {"total": 0, "collections": {}}

        # Mapear colecciones según niche_registry
        collections_map = {
            "restaurante": ["global_alimentos", "global_fiscal_mx", "global_legal_mx"],
            "contador": ["global_fiscal_mx", "global_legal_mx"],
            "pastelero": ["global_alimentos", "global_fiscal_mx"],
            "abogado": ["global_legal_mx", "global_fiscal_mx"],
            "constructor": ["global_construccion", "global_fiscal_mx"],
            "general": ["global_fiscal_mx", "global_legal_mx"],
        }
        collections = collections_map.get(niche, ["global_fiscal_mx"])

        for source_data in sources:
            source_name = source_data["source"]
            text = source_data["text"]
            chunks = self.chunk_text(text, source_name)

            for collection in collections:
                count = await self.upsert_chunks(collection, chunks, niche)
                self.stats[niche]["total"] += count
                if collection not in self.stats[niche]["collections"]:
                    self.stats[niche]["collections"][collection] = 0
                self.stats[niche]["collections"][collection] += count

    async def report_stats(self):
        """Reporte final."""
        logger.info("\n" + "="*70)
        logger.info("📊 REPORTE FINAL — SEED 6 NICHOS")
        logger.info("="*70)

        total_vectors = 0
        for niche, stats in self.stats.items():
            logger.info(f"\n{niche.upper()}: {stats['total']} vectores")
            for collection, count in stats['collections'].items():
                logger.info(f"  • {collection}: {count}")
            total_vectors += stats['total']

        logger.info("\n" + "-"*70)
        logger.info(f"TOTAL VECTORES UPSERTED: {total_vectors}")
        logger.info(f"TIMESTAMP: {datetime.now().isoformat()}")
        logger.info("="*70)

    async def run(self):
        """Ejecuta seed completo."""
        logger.info("\n" + "="*70)
        logger.info("SEED 6 NICHOS EN QDRANT — Iniciando")
        logger.info(f"Qdrant: {QDRANT_URL}")
        logger.info(f"Ollama: {OLLAMA_URL}")
        logger.info("="*70)

        await self.health_check()

        for niche in NICHOS_A_SEED:
            sources = DUMMY_SOURCES.get(niche, [])
            await self.seed_niche(niche, sources)

        await self.report_stats()


# ── MAIN ─────────────────────────────────────────────────
async def main():
    seeder = Seeder6Niches()
    await seeder.run()


if __name__ == "__main__":
    asyncio.run(main())
