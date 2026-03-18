#!/usr/bin/env python3
"""
seed_fourgea_docs.py — Indexa documentos específicos de Fourgea Mexico en Qdrant (fourgea_docs).

Incluye:
  - Perfil fiscal del cliente (RFC, régimen, obligaciones)
  - Productos y fracciones arancelarias habituales
  - Proveedores recurrentes y países de origen
  - Contexto para que el Brain responda con datos reales de Fourgea
"""

import os, sys, json, time
import urllib.request

API_URL  = os.getenv("API_URL", "http://localhost:8000")
QDRANT   = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA   = os.getenv("OLLAMA_URL", "http://ollama:11434")
EMBED_MODEL = "nomic-embed-text"

# ── Documentos específicos de Fourgea ─────────────────────────────────────────

DOCS = [
    {
        "id": "fourgea-perfil-fiscal",
        "topic": "perfil_cliente",
        "title": "Fourgea Mexico — Perfil Fiscal",
        "text": """FOURGEA MEXICO SA DE CV — PERFIL FISCAL
RFC: E080820LC2
Régimen fiscal: Persona Moral — Régimen General de Ley (601)
Actividad principal: Importación y distribución de filtros industriales para fluidos hidráulicos, neumáticos y lubricantes.
Domicilio fiscal: Hermosillo, Sonora, México. Código postal: 83000.
Obligaciones SAT:
- Declaración mensual IVA (día 17 de cada mes)
- Declaración mensual ISR provisional (día 17 de cada mes)
- DIOT mensual (proveedores nacionales y extranjeros)
- Declaración anual ISR personas morales (marzo del año siguiente)
- CFDI 4.0 obligatorio para todas las operaciones
- Padrón de Importadores activo (SAT)
Régimen aduanero: Importaciones definitivas (C1). Sin IMMEX.
Moneda principal: USD para compras de importación. MXN para ventas nacionales.""",
    },
    {
        "id": "fourgea-productos-fracciones",
        "topic": "comercio_exterior",
        "title": "Fourgea — Productos y Fracciones Arancelarias",
        "text": """FOURGEA MEXICO — FRACCIONES ARANCELARIAS HABITUALES
Productos principales: filtros industriales para fluidos hidráulicos, neumáticos y lubricantes.

Fracciones arancelarias más usadas:
- 8421.23.01 — Aparatos para filtrar aceites minerales en motores de combustión interna. IGI: 5%. Arancel TMEC: 0%.
- 8421.29.99 — Los demás aparatos para filtrar o depurar líquidos. IGI: 5-15%. Arancel TMEC/UE: 0%.
- 8421.39.99 — Los demás aparatos para filtrar o depurar gases. IGI: 5%.
- 7019.39.99 — Fibra de vidrio para filtros industriales. IGI: 10%.
- 3926.90.99 — Partes plásticas para filtros. IGI: 10-15%.

NOM aplicables:
- NOM-005-STPS-1998: Manejo de sustancias químicas (si filtro aplica).
- No hay NOM obligatoria específica para filtros industriales importados.

Países de origen habituales: China (sin TMEC, paga IGI general), Alemania/UE, Estados Unidos (TMEC, IGI=0%).""",
    },
    {
        "id": "fourgea-proveedores",
        "topic": "proveedores",
        "title": "Fourgea — Proveedores Habituales",
        "text": """FOURGEA MEXICO — PROVEEDORES HABITUALES DE IMPORTACIÓN
1. Parker Hannifin (EUA) — Filtros hidráulicos y neumáticos. Aplica TMEC. IGI=0%.
2. Donaldson Company (EUA) — Filtros industriales multipropósito. Aplica TMEC. IGI=0%.
3. Pall Corporation (EUA/Alemania) — Filtros de alta precisión. Aplica TMEC o TLC UE.
4. Proveedores China — Filtros genéricos. Sin tratado. IGI según fracción (5-15%).
5. Hydac (Alemania) — Filtros hidráulicos industriales. Aplica TLC México-UE. IGI reducido.

Incoterm habitual: FOB origen / CIF México.
Método de valoración en aduana: Método 1 (valor de transacción).
Agente aduanal: Contratado por pedimento.""",
    },
    {
        "id": "fourgea-calculos-tipicos",
        "topic": "calculos_fiscales",
        "title": "Fourgea — Cálculos Típicos de Importación",
        "text": """FOURGEA MEXICO — EJEMPLO CÁLCULO DE IMPORTACIÓN TÍPICA
Producto: Filtros hidráulicos Parker (EUA) | Fracción 8421.23.01
Valor FOB: $10,000 USD
Tipo de cambio DOF: $17.50 MXN/USD
Flete internacional: $500 USD
Seguro: $50 USD

Valor en Aduana = FOB + Flete + Seguro = $10,550 USD = $184,625 MXN
IGI (TMEC = 0%): $0
DTA: $839 MXN (cuota fija 2026)
IVA de importación (16%): $184,625 × 16% = $29,540 MXN

Total contribuciones: $30,379 MXN
IVA es 100% acreditable (Fourgea tiene actividades gravadas al 100%)

Ejemplo sin TMEC (China):
IGI 5% sobre $184,625 = $9,231 MXN adicional
Total contribuciones con China: $39,610 MXN""",
    },
    {
        "id": "fourgea-calendario-obligaciones",
        "topic": "calendario_fiscal",
        "title": "Fourgea — Calendario de Obligaciones Fiscales 2026",
        "text": """FOURGEA MEXICO — CALENDARIO FISCAL 2026
Mensual (día 17 de cada mes):
- Declaración de IVA: pago o saldo a favor.
- Declaración ISR provisional: pago provisional mensual.
- DIOT: relación de proveedores nacionales y extranjeros del mes anterior.

Trimestral:
- No aplica régimen especial de trimestral (persona moral).

Anual (marzo 2027 para ejercicio 2026):
- Declaración anual ISR personas morales.
- Conciliación contable-fiscal.

Cierre mensual interno (Nathaly):
- Verificar facturas de compra y venta registradas.
- Conciliar importaciones con pedimentos aduanales.
- Calcular IVA neto (cobrado - pagado).
- Generar reporte de contribuciones al socio (Marco).""",
    },
    {
        "id": "fourgea-iva-acreditamiento",
        "topic": "iva",
        "title": "Fourgea — Acreditamiento de IVA",
        "text": """FOURGEA MEXICO — REGLAS DE ACREDITAMIENTO DE IVA
Fourgea es una empresa con actividades 100% gravadas a tasa 16% (ventas de filtros industriales).
No tiene actividades exentas de IVA.

Por lo tanto:
- IVA cobrado en ventas nacionales: 16% acumulable.
- IVA pagado en compras nacionales: 100% acreditable.
- IVA pagado en importaciones: 100% acreditable (presentando pedimento como comprobante).
- No requiere prorrateo de IVA (LIVA Art. 5-C).

Requisitos para acreditar IVA de importación:
1. Pedimento aduanal pagado (clave C1 o similar definitiva).
2. Estar registrada en el Padrón de Importadores SAT.
3. La mercancía destinada a actividades gravadas.
4. IVA efectivamente pagado en la operación.""",
    },
]


def embed(text: str) -> list:
    payload = json.dumps({"model": EMBED_MODEL, "prompt": text[:2000]}).encode()
    req = urllib.request.Request(
        f"{OLLAMA}/api/embeddings",
        data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["embedding"]


def upsert(doc_id: int, vector: list, payload: dict):
    data = json.dumps({"points": [{"id": doc_id, "vector": vector, "payload": payload}]}).encode()
    req = urllib.request.Request(
        f"{QDRANT}/collections/fourgea_docs/points",
        data=data, headers={"Content-Type": "application/json"}, method="PUT"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def main():
    print("=== Seed fourgea_docs — Qdrant ===\n")
    total = 0
    for i, doc in enumerate(DOCS):
        print(f"  [{i+1}/{len(DOCS)}] {doc['title']}...", end=" ", flush=True)
        try:
            full_text = f"{doc['title']}\n\n{doc['text']}"
            vec = embed(full_text)
            upsert(
                doc_id=1000 + i,
                vector=vec,
                payload={
                    "doc_id": doc["id"],
                    "text": full_text[:600],
                    "title": doc["title"],
                    "topic": doc["topic"],
                    "fuente": "fourgea_interno",
                }
            )
            print("OK")
            total += 1
        except Exception as e:
            print(f"ERROR: {e}")
        time.sleep(1)

    print(f"\n✅ {total}/{len(DOCS)} documentos indexados en fourgea_docs")


if __name__ == "__main__":
    main()
