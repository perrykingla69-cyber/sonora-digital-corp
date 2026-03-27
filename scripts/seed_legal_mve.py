#!/usr/bin/env python3
"""
Seed de base legal MVE para Qdrant — fiscal_mx collection
Fuentes: Ley Aduanera, RGCE 2025, DOF, VUCEM, Incoterms

Uso:
  python3 seed_legal_mve.py --url https://sonoradigitalcorp.com/api --token <JWT>
"""

import argparse
import json
import logging
import uuid
import urllib.request
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# ─────────────────────────────────────────────────────────────────────────────
# BASE DE CONOCIMIENTO LEGAL — MVE / COMERCIO EXTERIOR
# Cada documento: {"id": str, "text": str, "metadata": dict}
# ─────────────────────────────────────────────────────────────────────────────

DOCS = []

def doc(fuente, titulo, texto, tags=None):
    DOCS.append({
        "id": str(uuid.uuid4()),
        "text": f"{titulo}\n\n{texto}",
        "metadata": {
            "fuente": fuente,
            "titulo": titulo,
            "tags": tags or [],
            "tema": "mve_aduanas",
        }
    })

# ─── LEY ADUANERA — Art. 59-A: MVE obligatoria ────────────────────────────

doc("Ley Aduanera", "Art. 59-A — Manifestación de Valor Obligatoria",
"""Las personas que tengan el carácter de importadores deberán presentar ante el agente o apoderado aduanal,
previamente al despacho de las mercancías, una manifestación de valor en documento electrónico en la que
declaren, bajo protesta de decir verdad, que los elementos que sirvieron para determinar el valor en aduana
de la mercancía son verídicos y que han expresado el precio pagado o por pagar en la operación de compra-venta
que dio origen a la importación, así como que han proporcionado todos los elementos que incrementan o
disminuyen el precio y que determinaron el valor en aduana.

La Manifestación de Valor debe presentarse:
- Para importaciones definitivas de mercancías
- A partir del 1 de abril de 2026, de forma digital a través de VUCEM
- Antes del despacho aduanal de las mercancías
- En idioma español, en pesos mexicanos o su equivalente en la moneda de la operación

El incumplimiento de esta obligación genera multa conforme al Art. 197 de esta Ley.""",
["mve", "obligacion", "importacion", "vucem"])

doc("Ley Aduanera", "Art. 197 — Multas por errores en Manifestación de Valor",
"""Las infracciones a las disposiciones sobre el valor en aduana se sancionan con:

Multa del 70% al 100% del valor de las contribuciones omitidas o del beneficio indebido cuando:
- El contribuyente declare un valor en aduana inferior al valor real de las mercancías
- Se omitan los ajustes incrementables (flete, seguro, regalías, etc.)
- Se declare un método de valoración incorrecto sin justificación
- La manifestación de valor contenga datos falsos o incompletos

Multa de $6,370 a $12,770 cuando:
- No se presente la Manifestación de Valor dentro del plazo establecido
- Se presente con información incompleta no subsanada

La autoridad aduanera puede retener las mercancías hasta en tanto se regularice la situación.
Reincidencia: duplicación de la multa aplicable.""",
["multa", "sancion", "infraccion", "valor_aduana"])

# ─── MÉTODOS DE VALORACIÓN Art. 45-50 ─────────────────────────────────────

doc("Ley Aduanera", "Art. 45 — Método 1: Valor de Transacción (el más común)",
"""El valor en aduana de las mercancías importadas será el valor de transacción de las mismas, es decir,
el precio pagado o por pagar por las mercancías cuando éstas se vendan para ser exportadas a territorio
nacional, siempre que concurran las siguientes circunstancias y condiciones:

1. Que no existan restricciones a la cesión o utilización de las mercancías por el comprador
2. Que la venta o el precio no dependan de condiciones cuyo valor no sea determinable
3. Que no revierta al vendedor parte alguna del producto de la reventa o de cualquier cesión posterior
4. Que no exista vinculación entre comprador y vendedor, o que dicha vinculación no haya influido en el precio

El precio pagado o por pagar comprende el total de los pagos efectuados o por efectuar por el comprador al
vendedor o en beneficio de éste, por las mercancías importadas. Este precio puede incluir pagos directos e
indirectos.

PRECIO PAGADO = valor de la factura comercial entre comprador y vendedor
AJUSTES INCREMENTABLES deben sumarse: flete, seguro, cargos de carga/descarga hasta lugar de importación,
costo de envases, embalajes, materiales/moldes provistos por comprador, regalías, ingresos de reventa.
AJUSTES DECREMENTABLES pueden restarse: fletes después de importación, derechos e impuestos en México,
intereses financieros.""",
["metodo_1", "valor_transaccion", "precio_pagado", "ajustes"])

doc("Ley Aduanera", "Art. 46-50 — Métodos 2-6: Valoración cuando no aplica Método 1",
"""Se deben aplicar en orden jerárquico. Solo se pasa al siguiente si el anterior no es aplicable.
El importador puede solicitar invertir el orden de los métodos 4 y 5.

MÉTODO 2 — Valor de transacción de mercancías IDÉNTICAS (Art. 46):
- Mercancías idénticas = misma naturaleza, características, calidad, marcas, país de producción
- Producidas por el mismo fabricante o uno diferente (como último recurso)
- Vendidas para exportar a México en el mismo tiempo o aproximado

MÉTODO 3 — Valor de transacción de mercancías SIMILARES (Art. 47):
- Mercancías similares = aunque no sean idénticas, tienen características y composición semejantes
- Cumplen las mismas funciones y son intercambiables comercialmente
- Mismas características de país de producción y tiempo de exportación que Método 2

MÉTODO 4 — Valor DEDUCTIVO (Art. 48):
- Se parte del precio de venta en México de las mercancías importadas, idénticas o similares
- Se deducen: comisiones, margen de utilidad, fletes y seguros, derechos e impuestos en México

MÉTODO 5 — Valor RECONSTRUIDO (Art. 49):
- Se suma: costo de producción + gastos generales y utilidades de país exportador + gastos de exportación
- Requiere documentación detallada del fabricante

MÉTODO 6 — ÚLTIMO RECURSO (Art. 50):
- Debe basarse en uno de los métodos anteriores con flexibilidad razonable
- No puede basarse en precios de venta en México de mercancías producidas en México
- No puede basarse en precios arbitrarios o ficticios

IMPORTANTE: El uso de Métodos 2-6 debe JUSTIFICARSE por escrito explicando por qué no aplica Método 1.""",
["metodo_2", "metodo_3", "metodo_4", "metodo_5", "metodo_6", "valoracion_alternativa"])

# ─── AJUSTES INCREMENTABLES Art. 65 ────────────────────────────────────────

doc("Ley Aduanera", "Art. 65 — Ajustes Incrementables al Valor de Transacción",
"""Para determinar el valor en aduana conforme al Art. 45, se adicionarán al precio pagado o por pagar
los siguientes elementos, en la medida en que corran a cargo del comprador y no estén incluidos en el precio:

a) Los gastos de transporte de las mercancías importadas, los gastos de carga y descarga y
   manipulación conexos con el transporte de las mercancías importadas hasta el puerto o lugar
   de importación — FLETE

b) El costo del seguro de las mercancías — SEGURO

c) Los gastos de carga, descarga y manipulación conexos con el transporte de las importadas
   hasta el recinto fiscal del punto de entrada al territorio nacional

d) El costo de los envases o embalajes (a menos que se traten como mercancías separadas)

e) Los materiales, piezas, elementos, partes, herramientas, moldes o matrices que el comprador
   haya suministrado directa o indirectamente sin cargo (o a precio reducido)

f) Los cánones y derechos de licencia (regalías) relativos a las mercancías que se importan,
   que el comprador esté obligado a pagar como condición de la venta

g) El valor de cualquier parte del producto de la reventa, cesión o utilización posterior
   que revierta directa o indirectamente al vendedor

INCOTERMS y ajustes:
- EXW/FCA/FAS/FOB: precio NO incluye flete ni seguro → DEBEN sumarse en la MVE
- CFR: precio incluye flete, no seguro → solo agregar seguro
- CIF/CIP/CPT: precio incluye flete y seguro → generalmente no se agregan
- DDP: precio incluye todo, incluyendo derechos → cuidado con doble tributación""",
["ajustes_incrementables", "flete", "seguro", "regalias", "incoterm_ajuste"])

# ─── VINCULACIÓN Art. 64 ────────────────────────────────────────────────────

doc("Ley Aduanera", "Art. 64 — Vinculación entre Comprador y Vendedor",
"""Se considerará que existe vinculación entre personas cuando:
a) Una de ellas ocupe cargos de dirección o responsabilidad en una empresa de la otra persona
b) Estén legalmente reconocidas como asociadas en negocios
c) Estén en relación de empleador y empleado
d) Una persona tenga, directa o indirectamente, la propiedad, el control o la posesión del 5% o más
   de las acciones o títulos en circulación con derecho a voto de ambas personas
e) Una de ellas controle directa o indirectamente a la otra
f) Ambas personas estén controladas directa o indirectamente por una tercera
g) Juntas controlen, directamente o indirectamente, a una tercera persona
h) Sean de la misma familia

Cuando haya vinculación, el valor de transacción (Método 1) PUEDE usarse si el importador demuestra que:
1. El precio no fue influido por la vinculación
2. El precio se aproxima mucho a uno de los "valores de prueba" (precio a compradores no vinculados,
   valor deductivo o reconstruido en el mismo período de tiempo)

La vinculación per se NO invalida el Método 1 — pero DEBE declararse y justificarse en la MVE.
Omitir la vinculación existente es una infracción grave sancionada con multa del 70-100%.""",
["vinculacion", "partes_relacionadas", "intercompany", "justificacion_vinculacion"])

# ─── FRACCIÓN ARANCELARIA ──────────────────────────────────────────────────

doc("RGCE / TIGIE", "Fracción Arancelaria — Cómo clasificar correctamente",
"""La fracción arancelaria es el código de 8-10 dígitos del Sistema Armonizado (SA) que clasifica
la mercancía. En México se usa la TIGIE (Tarifa de la Ley de los Impuestos Generales de Importación y Exportación).

FORMATO: DDDD.DD.DD.XX (ej: 8481.80.99.99)
- 4 primeros dígitos: Capítulo y Partida del SA
- 2 siguientes: Subpartida
- 2 siguientes: Fracción nacional
- 2 últimos: Complemento nacional

IMPORTANCIA en la MVE:
- Determina la tasa del IGI (Impuesto General de Importación)
- Determina si aplican regulaciones no arancelarias (permisos, NOM, cupos)
- Afecta las preferencias arancelarias (T-MEC, otros TLCs)
- Una fracción incorrecta puede resultar en multas y retención de mercancía

CÓMO VERIFICAR:
- Portal SAT: www.sat.gob.mx → comercio exterior → TIGIE
- VUCEM clasifica automáticamente si se proporciona descripción detallada
- El agente aduanal es responsable solidario de la clasificación correcta

ERRORES COMUNES:
- Usar fracción de producto similar pero distinto material (acero vs plástico)
- Usar fracción de producto terminado para partes/componentes
- No actualizar ante cambios en la TIGIE (revisión anual en DOF)""",
["fraccion_arancelaria", "tigie", "clasificacion_arancelaria", "igi"])

# ─── INCOTERMS 2020 en contexto aduanal México ────────────────────────────

doc("Incoterms 2020 / Ley Aduanera", "Incoterms y su impacto en el Valor en Aduana",
"""Los INCOTERMS (International Commercial Terms) definen las responsabilidades de comprador y vendedor.
En México, la aduana usa el valor CIF (Costo + Seguro + Flete) como base para el valor en aduana
cuando la mercancía llega por mar, o el valor equivalente para otros modos de transporte.

INCOTERMS VÁLIDOS (Incoterms 2020):
EXW — Ex Works: precio EN fábrica del vendedor. Comprador paga TODO el transporte.
      → MVE debe incluir flete internacional + seguro + carga/descarga como ajustes incrementables

FCA — Free Carrier: vendedor entrega al transportista designado por comprador.
      → MVE debe incluir flete internacional desde punto de entrega + seguro

FAS — Free Alongside Ship: vendedor entrega junto al buque en puerto de origen.
      → MVE debe incluir flete marítimo + seguro

FOB — Free On Board: vendedor carga en buque. Muy común en importaciones mexicanas.
      → MVE debe incluir flete internacional (desde puerto origen) + seguro

CFR — Cost and Freight: vendedor paga el flete, pero no el seguro.
      → MVE debe incluir solo el seguro como ajuste

CIF — Cost, Insurance and Freight: incluye flete Y seguro hasta puerto destino.
      → Precio ya incluye CIF; generalmente no se agregan ajustes

CPT — Carriage Paid To: similar a CFR pero para cualquier modo de transporte.
      → Igual que CIF para efectos de MVE

CIP — Carriage and Insurance Paid To: incluye transporte y seguro hasta destino.
      → Precio ya incluye CIF equivalente

DAP — Delivered at Place: entrega en lugar convenido, sin importación.
      → Precio incluye transporte pero no derechos; revisar si incluye seguro

DPU — Delivered at Place Unloaded: entrega con descarga en destino.
      → Igual que DAP más descarga

DDP — Delivered Duty Paid: vendedor paga todo incluyendo derechos en México.
      → Cuidado: puede generar doble tributación; consultar con agente aduanal""",
["incoterms", "fob", "cif", "exw", "valor_cif", "flete_seguro"])

# ─── VUCEM — Proceso de presentación ──────────────────────────────────────

doc("VUCEM / SAT", "VUCEM — Ventanilla Única: Presentar Manifestación de Valor",
"""VUCEM (Ventanilla Única de Comercio Exterior Mexicano) es el portal donde se presenta la MVE digital.

URL: www.ventanillaunica.gob.mx

REQUISITOS PREVIOS:
1. Firma Electrónica Avanzada (FIEL/e.firma) vigente del importador
2. Registro ante el Padrón de Importadores (SAT)
3. Número de pedimento asignado por el agente aduanal
4. Factura comercial digitalizada (PDF/XML)

PROCESO DE PRESENTACIÓN MVE:
1. Ingresar a VUCEM con FIEL
2. Módulo: Comercio Exterior → Manifestación de Valor
3. Capturar datos de la factura comercial y proveedor
4. Seleccionar método de valoración
5. Declarar ajustes incrementables (flete, seguro, etc.)
6. Declarar vinculación (si aplica)
7. Generar y firmar digitalmente con FIEL
8. VUCEM asigna un FOLIO único
9. Proporcionar el folio al agente aduanal para incluirlo en el pedimento

PLAZO: La MVE debe presentarse ANTES del despacho aduanal.
Para importaciones urgentes: existe la opción de presentar MVE provisional con garantía.

ERRORES FRECUENTES EN VUCEM:
- e.firma vencida o de persona diferente al importador registrado
- RFC del proveedor extranjero no en formato correcto (usar Tax ID del país origen)
- Fracción arancelaria no coincide con la del pedimento
- Valor declarado en moneda diferente a la de la factura sin tipo de cambio""",
["vucem", "presentacion", "folio_vucem", "efirma", "pedimento"])

# ─── PEDIMENTO ADUANAL ─────────────────────────────────────────────────────

doc("Ley Aduanera / RGCE", "Pedimento Aduanal — Relación con la MVE",
"""El PEDIMENTO es el documento oficial que ampara el despacho de mercancías en México.
Es elaborado por el Agente Aduanal autorizado por el SAT.

NÚMERO DE PEDIMENTO — Formato: AA/AAAA/NNNNNNN
- AA: clave de la aduana (ej: 04 = Nogales, 47 = Manzanillo, 10 = Ciudad Juárez)
- AAAA: año (ej: 2026)
- NNNNNNN: número consecutivo de la aduana (7 dígitos)
Ejemplo válido: 04/2026/1234567

RELACIÓN MVE-PEDIMENTO:
- El pedimento hace referencia al folio VUCEM de la MVE
- No puede presentarse pedimento sin MVE a partir del 1 abril 2026
- El valor declarado en la MVE DEBE coincidir con el valor en el pedimento
- Discrepancias entre MVE y pedimento → retención automática y multa

TIPOS DE PEDIMENTO más comunes:
- Clave A1: Importación definitiva (la más común, requiere MVE)
- Clave IN: Importación temporal (no siempre requiere MVE)
- Clave X1: Exportación definitiva (requiere MVE desde 1 abril 2026)
- Clave V1: Exportación temporal

CONTRIBUCIONES en el pedimento:
- IGI = valor en aduana × tasa arancelaria de la fracción
- IVA importación = (valor aduana + IGI + DTA + flete + seguro) × 16%
- DTA = $339 (cuota fija para A1 con TLC) o 8 al millar del valor aduana""",
["pedimento", "numero_pedimento", "aduana", "igi", "iva_importacion", "dta"])

# ─── RGCE 2025 — Reglas específicas MVE ───────────────────────────────────

doc("RGCE 2025", "Reglas Generales de Comercio Exterior 2025 — MVE Digital",
"""Las Reglas Generales de Comercio Exterior (RGCE) 2025 establecen los requisitos específicos
para la presentación de la Manifestación de Valor digital.

REGLA 1.9.19 — Manifestación de Valor por medio de documento electrónico:
Los importadores deberán presentar la manifestación de valor en documento electrónico a través
de la Ventanilla Digital del SAT (VUCEM), con anterioridad al despacho de las mercancías.

DATOS OBLIGATORIOS en la MVE digital (RGCE Apéndice 22):
1. RFC o Tax ID del importador
2. Nombre o razón social del importador
3. RFC o identificación fiscal del proveedor
4. Nombre o razón social del proveedor
5. País de origen de las mercancías
6. País de procedencia
7. Número y fecha de la factura comercial
8. Descripción detallada de la mercancía
9. Fracción arancelaria
10. Cantidad y unidad de medida
11. Precio unitario y total
12. Moneda de la transacción
13. Tipo de cambio aplicado
14. INCOTERM pactado
15. Método de valoración (1-6)
16. Ajustes incrementables (flete, seguro, regalías, etc.)
17. Declaración de vinculación (sí/no) y justificación si aplica
18. Valor en aduana en moneda nacional (pesos mexicanos)

INFORMACIÓN COMPLEMENTARIA requerida cuando aplica:
- Certificado de origen (para preferencias T-MEC/TLC)
- Contrato de compraventa internacional
- Lista de empaque (packing list)
- Documentos de transporte (BL, AWB, carta porte)
- Póliza de seguro""",
["rgce", "requisitos_mve", "datos_obligatorios", "apendice_22"])

# ─── T-MEC / PREFERENCIAS ARANCELARIAS ────────────────────────────────────

doc("T-MEC 2020", "T-MEC — Preferencias Arancelarias para Importaciones de USA y Canadá",
"""El T-MEC (Tratado entre México, Estados Unidos y Canadá, vigente desde julio 2020,
sustituto del TLCAN) otorga tasas preferenciales de arancel (0% en la mayoría de fracciones)
para mercancías originarias de Estados Unidos o Canadá.

PARA APLICAR PREFERENCIA T-MEC en la MVE:
1. La mercancía debe ser "originaria" del T-MEC (reglas de origen del Capítulo 4)
2. Debe presentarse Certificado de Origen (CO) válido
3. El CO puede ser emitido por: el exportador, productor o importador
4. Vigencia del CO: hasta 12 meses desde la fecha de emisión

DECLARACIÓN EN LA MVE:
- Indicar tasa preferencial 0% (o la tasa aplicable por fracción)
- Anotar que aplica preferencia T-MEC
- Tener disponible el CO por si la aduana lo solicita (no siempre se adjunta)

CUIDADO:
- Mercancías de China, Japón, Europa: NO aplica T-MEC → tasa del IGI normal (varía 0-35%)
- Reexportaciones: si el producto fue fabricado en China y solo pasó por USA, NO es originario T-MEC
- "Made in USA" no garantiza origen T-MEC; debe cumplir reglas de valor de contenido regional

OTRAS PREFERENCIAS:
- TLCUEM (México-Unión Europea): aplica a mercancías europeas
- AAE México-Japón: aplica a mercancías japonesas
- Revisar en VUCEM qué preferencias aplican por fracción arancelaria""",
["tmec", "tlcan", "origen", "certificado_origen", "preferencia_arancelaria"])

# ─── PREGUNTAS FRECUENTES MVE ──────────────────────────────────────────────

doc("FAQ / SAT", "Preguntas Frecuentes sobre MVE — Errores Comunes",
"""PREGUNTA: ¿Cuándo es obligatoria la MVE?
RESPUESTA: A partir del 1 de abril de 2026, para TODAS las importaciones y exportaciones definitivas
de mercancías comerciales en México. Antes de esa fecha era voluntaria.

PREGUNTA: ¿Qué pasa si me equivoco en la MVE?
RESPUESTA: Si el error se detecta ANTES del despacho, puede corregirse sin sanción.
Si se detecta DESPUÉS del despacho mediante auditoría, la multa es del 70-100% de contribuciones omitidas.

PREGUNTA: ¿La MVE reemplaza a la factura comercial?
RESPUESTA: No. La factura comercial sigue siendo el documento base. La MVE es una declaración
jurada adicional que confirma que el valor declarado en la factura es el real.

PREGUNTA: ¿Quién firma la MVE?
RESPUESTA: El importador, con su FIEL/e.firma vigente. No el agente aduanal.
El importador es responsable de la veracidad de los datos.

PREGUNTA: ¿El agente aduanal puede presentar la MVE por mí?
RESPUESTA: Solo si tiene poder notarial para actuar en nombre del importador. La firma digital
del importador es obligatoria; no puede delegarse sin poder legal.

PREGUNTA: ¿Qué método de valoración debo usar?
RESPUESTA: El 95% de las operaciones comerciales normales usan Método 1 (valor de transacción).
Solo se usa otro método cuando no existe una venta real (donaciones, muestras, consignación, etc.)

PREGUNTA: ¿Qué valor se declara para mercancías donadas o sin costo?
RESPUESTA: Se usa el valor de mercado en el país de exportación. Se aplica Método 3 (similares)
o Método 4 (deductivo). Siempre requiere justificación escrita.

PREGUNTA: ¿Cómo afecta el tipo de cambio?
RESPUESTA: Se usa el tipo de cambio del DOF del día de la presentación del pedimento.
Si la factura es en USD, se multiplica por el tipo de cambio DOF para obtener el valor en MXN.""",
["faq", "errores_comunes", "obligacion", "firma_electronica", "tipo_cambio"])

# ─── CONTRIBUCIONES: IGI, IVA, DTA ────────────────────────────────────────

doc("Ley Aduanera / CFF", "Cálculo de Contribuciones en Importación: IGI, IVA, DTA",
"""Las contribuciones a pagar en una importación definitiva son:

1. IGI — Impuesto General de Importación
   = Valor en Aduana × Tasa arancelaria de la fracción (TIGIE)
   - Tasa varía: 0% (T-MEC/TLC), 5%, 10%, 15%, 20%, 25% o más según fracción y origen
   - Base: VALOR EN ADUANA (valor CIF en pesos mexicanos)

2. IVA Importación (Art. 24 LIVA)
   = (Valor en Aduana + IGI + DTA + Otras contribuciones) × 16%
   - Se ACREDITA contra IVA causado en ventas (es un IVA acreditable)
   - Las empresas con actividad gravada recuperan este IVA en su declaración mensual

3. DTA — Derecho de Trámite Aduanero (Art. 49 LFD)
   = 8 al millar del valor en aduana (mínimo $339 MXN aprox.)
   Excepto: Con T-MEC aplica cuota fija reducida (~$339 MXN por operación)

EJEMPLO PRÁCTICO:
- Mercancía China FOB $10,000 USD
- Tipo cambio: $17.50 MXN/USD
- Flete y seguro CIF: $800 USD adicionales
- Valor en aduana: $10,800 USD × $17.50 = $189,000 MXN
- Fracción con IGI 10%: $189,000 × 10% = $18,900 IGI
- DTA (8 al millar): $189,000 × 0.008 = $1,512 DTA
- IVA: ($189,000 + $18,900 + $1,512) × 16% = $33,505 IVA
- Total contribuciones: $53,917 MXN""",
["igi", "iva_importacion", "dta", "contribuciones", "calculo_impuestos"])

# ─── FOURGEA — CONTEXTO ESPECÍFICO ────────────────────────────────────────

doc("Fourgea México", "Fourgea México SA de CV — Perfil de Importaciones",
"""Fourgea México SA de CV
RFC: FME080820LC2
Giro: Filtración y purificación de fluidos industriales

PRODUCTOS QUE IMPORTA Fourgea:
- Filtros industriales para fluidos hidráulicos, lubricantes y combustibles
- Elementos filtrantes (cartuchos, bolsas filtrantes)
- Válvulas de control y accesorios hidráulicos
- Equipos de purificación de aceite industrial
- Separadores agua-aceite

FRACCIONES ARANCELARIAS FRECUENTES para el giro de Fourgea:
- 8421.29.99: Aparatos para filtrar o depurar líquidos (filtros industriales)
- 8421.39.99: Aparatos para filtrar o depurar gases
- 8481.80.99: Válvulas para oleoductos, tuberías y calderas
- 8484.10.01: Juntas metálicas planas (empaques)
- 3926.90.99: Manufacturas de plástico (cartuchos de filtro)
- 5911.40.01: Telas para filtros técnicos

ORIGEN más frecuente de proveedores:
- USA (aplica T-MEC si hay certificado de origen)
- Alemania (aplica TLCUEM con CO)
- China (IGI normal, sin preferencia; verificar antidumping)

MÉTODOS DE PAGO típicos en el sector:
- 30/60/90 días desde embarque (Método 1 aplica directamente)
- Open Account con proveedores recurrentes
- L/C para nuevos proveedores""",
["fourgea", "filtros_industriales", "fracciones_fourgea", "importaciones_fourgea"])


# ─────────────────────────────────────────────────────────────────────────────
# CARGA A QDRANT via API
# ─────────────────────────────────────────────────────────────────────────────

def post_batch(url, token, docs, context="fiscal"):
    data = json.dumps({"docs": docs, "context": context}).encode()
    req = urllib.request.Request(
        f"{url}/brain/index/batch",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://sonoradigitalcorp.com/api")
    parser.add_argument("--token", required=True, help="JWT token")
    parser.add_argument("--batch-size", type=int, default=5)
    args = parser.parse_args()

    logging.info(f"Indexando {len(DOCS)} documentos legales en Qdrant...")
    logging.info(f"URL: {args.url}")

    BATCH = args.batch_size
    ok = 0
    for i in range(0, len(DOCS), BATCH):
        batch = DOCS[i:i+BATCH]
        try:
            r = post_batch(args.url, args.token, batch)
            ok += r.get("indexed", len(batch))
            logging.info(f"  [{i+len(batch)}/{len(DOCS)}] ✓ {r}")
        except Exception as e:
            logging.error(f"  [{i+len(batch)}/{len(DOCS)}] ERROR: {e}")

    logging.info(f"Total indexados: {ok}/{len(DOCS)}")


if __name__ == "__main__":
    main()
