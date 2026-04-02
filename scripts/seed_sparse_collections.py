#!/usr/bin/env python3
"""
seed_sparse_collections.py — Agrega vectores de conocimiento a colecciones escasas en Qdrant.

Colecciones objetivo: ventas_mx, logistica_mx, admin_mx, rrhh_mx, aduanas_mx
Usa nomic-embed-text via Ollama para embeddings.
Qdrant: http://localhost:6333

Uso:
    python3 scripts/seed_sparse_collections.py
    python3 scripts/seed_sparse_collections.py --collections ventas_mx,admin_mx
"""

import json
import urllib.request
import uuid
import argparse
import sys
import time

OLLAMA_URL = "http://localhost:11434"
QDRANT_URL = "http://localhost:6333"
EMBED_MODEL = "nomic-embed-text"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def embed(text: str) -> list[float]:
    """Genera embedding con nomic-embed-text via Ollama."""
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embeddings",
        data=json.dumps({"model": EMBED_MODEL, "prompt": text}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["embedding"]


def upsert(collection: str, text: str, metadata: dict) -> dict:
    """Inserta un punto en Qdrant con su embedding."""
    vec = embed(text)
    point = {
        "id": str(uuid.uuid4()),
        "vector": vec,
        "payload": {**metadata, "text": text},
    }
    req = urllib.request.Request(
        f"{QDRANT_URL}/collections/{collection}/points",
        data=json.dumps({"points": [point]}).encode(),
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def get_points_count(collection: str) -> int:
    req = urllib.request.Request(f"{QDRANT_URL}/collections/{collection}")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())["result"]["points_count"]


# ─── Conocimiento por colección ───────────────────────────────────────────────

KNOWLEDGE = {

    "ventas_mx": [
        {
            "title": "Facturación CFDI 4.0 en ventas a clientes",
            "text": (
                "El CFDI 4.0 (Comprobante Fiscal Digital por Internet) es obligatorio para toda venta en México desde enero 2023. "
                "El emisor debe incluir: RFC del receptor, nombre completo o razón social, código postal del domicilio fiscal del receptor, "
                "régimen fiscal del receptor y uso del CFDI (por ejemplo G01 para adquisición de mercancias, G03 para gastos en general). "
                "La clave de producto o servicio del catálogo del SAT (SAT-ClaveProdServ) debe corresponder exactamente al bien vendido. "
                "El complemento de pagos (versión 2.0) es necesario cuando el pago se realiza en parcialidades o en fecha posterior a la emisión."
            ),
            "topic": "facturacion",
            "fuente": "SAT CFDI 4.0",
        },
        {
            "title": "IVA en ventas: tasa general y tasa cero",
            "text": (
                "En México el IVA general aplicable a ventas es del 16%. Existen actos gravados a tasa 0%, como exportación de bienes, "
                "alimentos en estado natural (frutas, verduras, carne, leche), medicamentos de patente, y libros o revistas. "
                "Los contribuyentes con ingresos por actos gravados a tasa 0% tienen derecho al acreditamiento o devolución del IVA causado. "
                "Las ventas exentas (como intereses de créditos hipotecarios para casa habitación) no generan IVA trasladado ni permiten "
                "acreditamiento proporcional del IVA de gastos relacionados. Es crucial distinguir entre tasa cero y exento para efectos "
                "del acreditamiento."
            ),
            "topic": "iva_ventas",
            "fuente": "LIVA Arts. 1, 2-A, 9",
        },
        {
            "title": "Descuentos y bonificaciones fiscales en ventas",
            "text": (
                "Los descuentos y bonificaciones otorgados sobre el precio pactado pueden reducir la base del IVA e ISR, siempre que "
                "estén debidamente soportados con un CFDI de egreso (nota de crédito). El CFDI de egreso debe relacionarse al CFDI de "
                "ingreso original mediante el campo UUID. Los descuentos en factura al momento de la venta se registran directamente en "
                "el comprobante. Las bonificaciones posteriores (retroactivas) requieren nota de crédito emitida en el mismo ejercicio "
                "fiscal o máximo dentro de los primeros tres meses del siguiente para ser deducibles en el ejercicio en que se otorgaron."
            ),
            "topic": "descuentos_fiscales",
            "fuente": "LISR Art. 25 fracc. IV, CFF",
        },
        {
            "title": "Contrato de compraventa mercantil en México",
            "text": (
                "El contrato de compraventa mercantil en México se rige por el Código de Comercio (Arts. 371-409). Elementos esenciales: "
                "precio cierto en dinero, cosa determinada y consentimiento de las partes. Para bienes inmuebles o contratos mayores a "
                "determinado monto conviene formalizarlo ante notario. Las condiciones de pago (crédito, contado, parcialidades), garantías "
                "de evicción y vicios ocultos deben estipularse con claridad. En operaciones B2B se recomienda incluir cláusula de "
                "reserva de dominio hasta liquidación total, pena convencional por incumplimiento y jurisdicción pactada."
            ),
            "topic": "contratos_ventas",
            "fuente": "Código de Comercio",
        },
        {
            "title": "Gestión de cobranza y cartera vencida en PYMEs",
            "text": (
                "La cartera vencida se registra contablemente cuando una cuenta por cobrar supera el plazo pactado de crédito. "
                "Para efectos fiscales (ISR), las pérdidas por cuentas incobrables son deducibles si: la deuda es mayor a 30,000 UDIS "
                "y existe sentencia firme de insolvencia del deudor, o si es menor y ha transcurrido más de un año desde el vencimiento "
                "sin cobro. El acreedor debe notificar al SAT el monto y datos del deudor mediante CFDI de egreso. "
                "En CRM para PYMEs, conviene automatizar alertas de vencimiento a 30, 60 y 90 días, generar estados de cuenta automáticos "
                "y documentar cada gestión de cobro para soportar la deducción por incobrable."
            ),
            "topic": "cobranza_cartera",
            "fuente": "LISR Art. 28 fracc. XVI",
        },
        {
            "title": "CRM para PYMEs mexicanas: seguimiento de pipeline",
            "text": (
                "Un CRM (Customer Relationship Management) para PYME mexicana debe contemplar: etapas del pipeline (prospecto, cotización, "
                "negociación, cierre, posventa), registro del RFC del cliente para precarga del CFDI, historial de compras con UUID de "
                "facturas relacionadas, y alertas de renovación o venta cruzada. La integración con facturación electrónica permite "
                "emitir CFDI directamente desde la oportunidad ganada. Para el SAT, mantener el expediente de cliente (contrato, "
                "cotizaciones, facturas) durante al menos 5 años es obligatorio para soportar deducciones y acreditamiento de IVA."
            ),
            "topic": "crm_pyme",
            "fuente": "Buenas prácticas comerciales MX",
        },
        {
            "title": "Políticas de precios y margen en ventas B2B México",
            "text": (
                "En ventas entre partes relacionadas (B2B), el SAT puede revisar si los precios de transferencia se pactaron a "
                "valor de mercado (arm's length). Para PYMEs no relacionadas, la política de precios debe considerar: costo directo, "
                "gastos indirectos asignables, margen de utilidad esperado y condiciones del mercado. Documentar la lista de precios "
                "vigente y cualquier descuento especial aprobado por gerencia ayuda a demostrar que no hubo subcosto que pudiera "
                "interpretarse como regalía encubierta o triangulación. El precio pactado en contrato debe coincidir con el CFDI emitido."
            ),
            "topic": "politica_precios",
            "fuente": "LISR Precios de Transferencia",
        },
    ],

    "logistica_mx": [
        {
            "title": "Carta Porte CFDI: obligatoriedad y estructura",
            "text": (
                "El Complemento Carta Porte (versión 3.1 vigente desde 2024) es obligatorio para el traslado de bienes y mercancías "
                "por territorio nacional. Aplica a transportistas y a propietarios que trasladen sus propios bienes en vehículo propio "
                "o arrendado. Datos requeridos: RFC transportista, operador (nombre y licencia), unidad vehicular (placa y modalidad), "
                "origen y destino con coordenadas, mercancías (clave SAT, peso bruto, unidad), y número de carta porte. "
                "El CFDI con Carta Porte debe emitirse antes de iniciar el traslado y portarse durante todo el recorrido. "
                "Sin este complemento, la mercancía puede ser retenida en revisión de la autoridad."
            ),
            "topic": "carta_porte",
            "fuente": "SAT Complemento Carta Porte 3.1",
        },
        {
            "title": "Pedimentos de importación: clasificación arancelaria y pago",
            "text": (
                "El pedimento de importación es el documento aduanal que ampara la legal estancia de mercancía extranjera en México. "
                "Se clasifica por tipo: A1 (importación definitiva), T1 (temporal para retornar), entre otros. "
                "La fracción arancelaria (8 dígitos) determina el arancel (Ad Valorem, específico o mixto), el IVA (16% o 0%), "
                "y las regulaciones no arancelarias aplicables (permisos, NOM, cuotas compensatorias). "
                "La base gravable es el valor en aduana: valor de transacción + seguro + flete (CIF). "
                "El agente aduanal certificado es obligatorio para importaciones comerciales; el importador puede actuar en su nombre "
                "solo en casos específicos (régimen simplificado de hasta 1,000 USD)."
            ),
            "topic": "pedimentos_importacion",
            "fuente": "LA Arts. 36-A, 64",
        },
        {
            "title": "Almacenes generales de depósito y almacenamiento fiscal en México",
            "text": (
                "Los Almacenes Generales de Depósito (AGD) son entidades autorizadas por la CNBV que emiten certificados de depósito "
                "y bonos de prenda como títulos de crédito que representan las mercancías almacenadas. El almacenamiento fiscal "
                "permite diferir el pago de aranceles e impuestos en importación mientras la mercancía permanece en el almacén bajo "
                "control aduanal. Es útil para empresas con alta rotación de inventario importado o que redistribuyen a múltiples "
                "destinos. Los costos de almacenamiento, maniobras y seguros son deducibles para ISR cuando están debidamente "
                "facturados con CFDI."
            ),
            "topic": "almacenamiento_fiscal",
            "fuente": "LGTOC, LA",
        },
        {
            "title": "NOM-045 y normas aplicables al transporte de carga en México",
            "text": (
                "La NOM-045-SCT2 establece las condiciones mínimas de seguridad para el transporte de carga terrestre. "
                "Cubre: pesos y dimensiones máximas de vehículos, condiciones mecánicas y eléctricas, documentación a bordo "
                "(licencia federal, tarjeta de circulación, seguro de responsabilidad civil, carta de porte). "
                "Para transporte de materiales y residuos peligrosos aplica además la NOM-002-SCT/2011 y la hoja de seguridad MSDS. "
                "El incumplimiento puede resultar en multas de hasta 200 veces el salario mínimo diario, retención del vehículo "
                "y responsabilidad civil por daños."
            ),
            "topic": "nom_transporte",
            "fuente": "NOM-045-SCT2, SCT",
        },
        {
            "title": "Cross-docking y centros de distribución en logística mexicana",
            "text": (
                "El cross-docking es una estrategia de distribución en la que la mercancía recibida en el almacén se transfiere "
                "directamente a los vehículos de salida sin almacenamiento prolongado. Reduce costos de manejo y tiempo de ciclo. "
                "En México, los CEDIS (Centros de Distribución) de grandes retailers como OXXO, Walmart o Amazon usan este modelo. "
                "Para PYMEs, el cross-docking es viable a través de operadores logísticos 3PL. "
                "Fiscalmente, cada traslado debe ampararse con su propio CFDI con Carta Porte. "
                "El control de inventario en tránsito debe reflejarse en contabilidad en la cuenta de mercancías en tránsito "
                "hasta que el receptor confirme la recepción."
            ),
            "topic": "cross_docking",
            "fuente": "Buenas prácticas logísticas MX",
        },
        {
            "title": "Cadena de frío y logística especializada en México",
            "text": (
                "La cadena de frío abarca el conjunto de procesos de almacenamiento y transporte de productos perecederos "
                "(alimentos, medicamentos, biológicos) a temperaturas controladas. En México la NOM-059-SSA1 regula los "
                "medicamentos biotecnológicos y su cadena de frío. Para alimentos, la NOM-251-SSA1 establece las BPM. "
                "Las unidades refrigeradas deben contar con termógrafo calibrado y registro continuo de temperatura. "
                "El CFDI con Carta Porte para estas cargas debe indicar las condiciones especiales de manejo (temperatura mínima "
                "y máxima). La ruptura de cadena de frío puede implicar responsabilidad civil y fiscal si la mercancía se daña "
                "y se pretende deducir como merma."
            ),
            "topic": "cadena_frio",
            "fuente": "NOM-059-SSA1, NOM-251-SSA1",
        },
    ],

    "admin_mx": [
        {
            "title": "Acta constitutiva de sociedad mercantil en México",
            "text": (
                "El acta constitutiva es el documento notarial que da origen a una persona moral mercantil en México. "
                "Debe otorgarse ante Notario Público e inscribirse en el Registro Público de Comercio (RPC). "
                "Contenido mínimo según LGSM: nombre/razón social, objeto social, duración, domicilio social, capital social "
                "(fijo y variable), órgano de administración (consejo o administrador único), vigilancia (comisario), "
                "asambleas y reglas de liquidación. La SA de CV requiere mínimo 2 socios y capital mínimo de $50,000 MXN suscrito "
                "($25,000 exhibido). La SAS (Sociedad por Acciones Simplificada) puede constituirse en línea vía SE con un solo socio "
                "y sin capital mínimo, pero con ingresos anuales limitados a 5 millones de pesos."
            ),
            "topic": "acta_constitutiva",
            "fuente": "LGSM, SE",
        },
        {
            "title": "RFC persona moral: obtención y actualización ante el SAT",
            "text": (
                "El RFC (Registro Federal de Contribuyentes) de persona moral se tramita ante el SAT una vez inscrita la sociedad "
                "en el RPC. Para SA de CV o SAPI: presentar acta constitutiva con sello del RPC, poder notarial del representante "
                "legal, identificación oficial del representante y comprobante de domicilio fiscal. "
                "El domicilio fiscal debe ser un lugar físico donde el contribuyente realiza actividades o tiene su administración "
                "principal; no puede ser un buzón postal ni domicilio de contador. "
                "El SAT puede verificar el domicilio y, si no lo localiza, reclasificar al contribuyente como no localizado, "
                "lo que genera restricción del certificado de sello digital (CSD) para facturar."
            ),
            "topic": "rfc_persona_moral",
            "fuente": "CFF Arts. 27, 10",
        },
        {
            "title": "Poder notarial: tipos y alcances en México",
            "text": (
                "El poder notarial es el instrumento por el cual una persona (poderdante) otorga facultades a otra (apoderado) "
                "para actuar en su nombre. Tipos principales: "
                "1) Poder general para actos de dominio — facultades amplias incluyendo enajenar bienes (el más amplio). "
                "2) Poder general para actos de administración — gestión ordinaria del negocio. "
                "3) Poder especial — para acto(s) específico(s) determinado(s). "
                "4) Poder para pleitos y cobranzas — representación en juicios. "
                "En personas morales, los poderes se otorgan mediante acuerdo del órgano de administración o asamblea. "
                "Para operaciones bancarias, aduanales o ante dependencias gubernamentales suele requerirse poder especial con "
                "cláusulas expresamente señaladas."
            ),
            "topic": "poder_notarial",
            "fuente": "CCF Arts. 2554-2587",
        },
        {
            "title": "Razón social y denominación social en México",
            "text": (
                "La razón social identifica a una sociedad de personas (ej. SNC, SC) usando nombres de los socios. "
                "La denominación social identifica a sociedades de capital (SA, SRL, SAS) con un nombre libre. "
                "Ambas deben ser distintas de cualquier otra sociedad registrada (verificar en el RPC y en el sistema SIGER de SE). "
                "La razón o denominación debe ir seguida del tipo societario (SA de CV, SRL de CV, etc.) y puede incluir siglas. "
                "Cambiar la razón social requiere asamblea extraordinaria, protocolización notarial e inscripción en el RPC. "
                "Fiscalmente implica actualizar el RFC, los CSD para facturación y todos los contratos vigentes."
            ),
            "topic": "razon_social",
            "fuente": "LGSM Arts. 2, 87, 59",
        },
        {
            "title": "Cambio de objeto social y reforma de estatutos",
            "text": (
                "El objeto social delimita las actividades que puede realizar la sociedad. Cambiarlo requiere: "
                "1) Convocatoria a Asamblea Extraordinaria de Accionistas. "
                "2) Quórum calificado (generalmente 75% del capital según estatutos). "
                "3) Protocolización del acta ante Notario Público. "
                "4) Inscripción en el RPC. "
                "5) Actualización del RFC ante el SAT (actividades económicas). "
                "Un objeto social demasiado restrictivo puede impedir deducir gastos de actividades conexas. "
                "Se recomienda un objeto social amplio que incluya la actividad principal y actividades complementarias o derivadas."
            ),
            "topic": "cambio_objeto_social",
            "fuente": "LGSM Arts. 182, 194",
        },
        {
            "title": "Domicilio fiscal: obligaciones y consecuencias del cambio",
            "text": (
                "El domicilio fiscal para personas morales es el lugar donde se encuentra la administración principal del negocio "
                "o el establecimiento donde se realizan las actividades. Obligaciones: mantenerlo actualizado en el SAT (portal), "
                "conservar documentación que acredite la permanencia en el domicilio (contratos de arrendamiento, facturas de "
                "servicios). Cambiar domicilio fiscal requiere aviso al SAT dentro de los 10 días hábiles siguientes al cambio. "
                "Si el SAT no puede localizar al contribuyente en su domicilio declarado, puede emitir una opinión de no localizado "
                "y restringir el CSD, impidiendo la emisión de CFDI."
            ),
            "topic": "domicilio_fiscal",
            "fuente": "CFF Art. 10, 27",
        },
    ],

    "rrhh_mx": [
        {
            "title": "Cuotas patronales IMSS: cálculo y conceptos 2026",
            "text": (
                "Las cuotas patronales al IMSS se calculan sobre el Salario Base de Cotización (SBC), topado en 25 UMAs diarias. "
                "Ramas y porcentajes patronales 2026 aproximados: "
                "Enfermedad y maternidad (cuota fija): 20.40% de 1 UMA por trabajador diario. "
                "Excedente prestaciones en especie (sobre SBC mayor a 3 UMAs): 1.10%. "
                "Gastos médicos pensionados: 1.05% del SBC. "
                "Riesgos de trabajo: clase I entre 0.54355% hasta clase V 7.58875% (según siniestralidad). "
                "Invalidez y vida: 1.75% del SBC. "
                "Guarderías y prestaciones sociales: 1.00% del SBC. "
                "Retiro (SAR): 2.00% del SBC — cuota patronal al IMSS. "
                "Cesantía y vejez: 3.150% del SBC (patron). "
                "INFONAVIT: 5.00% del SBC. "
                "El bimestre de pago es en los primeros 17 días naturales después del bimestre vencido."
            ),
            "topic": "cuotas_imss",
            "fuente": "LSS, LINFONAVIT 2026",
        },
        {
            "title": "PTU: participación de los trabajadores en las utilidades 2026",
            "text": (
                "La PTU equivale al 10% de la renta gravable de la empresa determinada conforme a la LISR. "
                "Límite máximo individual: el mayor entre 3 meses de salario o el promedio de PTU recibida en los últimos 3 años. "
                "Distribución: 50% se reparte en partes iguales entre todos los trabajadores con derecho; "
                "el otro 50% proporcional a los días laborados. "
                "Plazo de pago: empresas tienen 60 días a partir de la fecha límite de pago de la declaración anual ISR "
                "(mayo personas morales → PTU a más tardar el 31 de mayo). "
                "Trabajadores excluidos: directores, administradores, gerentes generales con acceso a información confidencial. "
                "La PTU no pagada en plazo genera IMSS e ISR al retenerse en nómina."
            ),
            "topic": "ptu",
            "fuente": "LFT Art. 117-131, LISR",
        },
        {
            "title": "Finiquito vs liquidación en México: diferencias y cálculo",
            "text": (
                "Finiquito: procede cuando el trabajador renuncia o se rescinde la relación sin responsabilidad patronal. "
                "Incluye: parte proporcional de vacaciones no gozadas, prima vacacional (25% mínimo), aguinaldo proporcional, "
                "partes alícuotas de cualquier prestación pendiente. "
                "Liquidación: procede cuando el patrón rescinde sin causa justificada o por causas de fuerza mayor. "
                "Además del finiquito incluye: 3 meses de salario integrado (indemnización constitucional) + 20 días por año "
                "trabajado. El salario integrado incluye cuotas diarias más partes proporcionales de: aguinaldo (15 días mínimo), "
                "vacaciones y prima vacacional. Toda entrega de finiquito o liquidación debe constar en documento firmado y "
                "de preferencia ante la JFCA o CAL para liberar al patrón de demandas futuras."
            ),
            "topic": "finiquito_liquidacion",
            "fuente": "LFT Arts. 47, 49, 50, 52, 84",
        },
        {
            "title": "Tabla ISR para asalariados 2026: retención mensual",
            "text": (
                "El ISR de asalariados se retiene conforme a las tablas del Anexo 8 de la RMF 2026. "
                "Tramos mensuales aproximados 2026: "
                "Hasta $8,952 MXN: 1.92%. "
                "$8,952 a $75,984: cuota fija $172 + 6.40% sobre excedente. "
                "$75,984 a $133,536: $4,461 + 10.88% sobre excedente. "
                "$133,536 a $155,232: $10,672 + 16.00% sobre excedente. "
                "$155,232 a $185,856: $14,144 + 17.92% sobre excedente. "
                "$185,856 a $374,496: $19,632 + 21.36% sobre excedente. "
                "Más de $374,496: $59,908 + 30.00% sobre excedente. "
                "El subsidio al empleo (tabla mensual) se aplica a trabajadores con ingresos mensuales hasta $10,171. "
                "El cálculo anual ajusta las retenciones y puede generar diferencias a favor del trabajador o del fisco."
            ),
            "topic": "tabla_isr_asalariados",
            "fuente": "RMF 2026 Anexo 8, LISR Art. 96",
        },
        {
            "title": "Contrato colectivo de trabajo en México",
            "text": (
                "El Contrato Colectivo de Trabajo (CCT) es el convenio celebrado entre el sindicato titular y el patrón para "
                "establecer condiciones de trabajo. Requiere registro ante el Centro Federal de Conciliación y Registro Laboral (CFCRL). "
                "El CCT debe revisarse cada 2 años en condiciones de trabajo y cada año en materia de salarios. "
                "La empresa no puede modificar unilateralmente condiciones del CCT. "
                "En empresas sin sindicato, el Reglamento Interior de Trabajo (RIT) regula la organización interna; "
                "debe depositarse ante la JFCA. "
                "La reforma laboral de 2023 fortaleció la democracia sindical: las revisiones del CCT requieren voto personal, "
                "libre, directo y secreto de los trabajadores."
            ),
            "topic": "contrato_colectivo",
            "fuente": "LFT Arts. 386-403, Reforma Laboral 2023",
        },
        {
            "title": "INFONAVIT: cuotas patronales, créditos y descuentos en nómina",
            "text": (
                "El patrón debe enterar al INFONAVIT el 5% del SBC de cada trabajador bimestralmente. "
                "Cuando un trabajador tiene crédito INFONAVIT activo, el patrón también retiene y entera el descuento del crédito "
                "según el Factor Descuento o número de VSM indicado en el aviso de retención. "
                "Desde 2024, los descuentos pueden ser en pesos fijos (Crédito en Pesos) o en VSM (Veces Salario Mínimo). "
                "El patrón es responsable solidario si omite retener y enterar. "
                "La aportación patronal 5% genera el fondo de vivienda del trabajador; si no usa crédito, "
                "puede retirarlo al pensionarse. Nuevos créditos INFONAVIT en 2026 tienen tasas fijas entre 4% y 12% según salario."
            ),
            "topic": "infonavit",
            "fuente": "LINFONAVIT, IMSS-INFONAVIT 2026",
        },
    ],

    "aduanas_mx": [
        {
            "title": "Reglas de Carácter General en Materia de Comercio Exterior 2026 (RCGMCE)",
            "text": (
                "Las RCGMCE son emitidas anualmente por el SAT y complementan la Ley Aduanera y el Código Fiscal. "
                "Para 2026 mantienen disposiciones clave: obligatoriedad del CFDI con Carta Porte para traslado nacional, "
                "actualización del padrón de importadores vía e.firma, uso obligatorio del Nuevo Esquema de Empresa Certificada (NEEC) "
                "para operadores autorizados. Regla 1.2.2 regula la firma electrónica avanzada para trámites aduanales. "
                "Las importaciones definitivas de mercancías de la lista de mercancías sujetas a precio estimado deben declarar "
                "valor conforme a los precios publicados en el DOF."
            ),
            "topic": "rcgmce_2026",
            "fuente": "RCGMCE 2026, DOF",
        },
        {
            "title": "PROSEC: Programa de Promoción Sectorial para reducción arancelaria",
            "text": (
                "El PROSEC (Programa de Promoción Sectorial) permite importar insumos y maquinaria con arancel preferencial "
                "(generalmente 0%) para empresas fabricantes de productos en sectores autorizados (electrónica, automotriz, "
                "textil, calzado, entre otros). La autorización se tramita ante la SE. "
                "El beneficio aplica solo a las fracciones arancelarias específicas del sector y solo al importador autorizado. "
                "Requiere demostrar que los insumos importados se incorporan a los productos fabricados. "
                "En 2025-2026 el gobierno actualizó los sectores elegibles. Importar con PROSEC sin autorización vigente "
                "constituye una infracción aduanera con multa del 130% de las contribuciones omitidas."
            ),
            "topic": "prosec",
            "fuente": "Decreto PROSEC, SE",
        },
        {
            "title": "IMMEX: Maquiladora e Industria Manufacturera de Exportación",
            "text": (
                "El Programa IMMEX permite importar temporalmente insumos, maquinaria y equipo sin pago de aranceles e IVA, "
                "condicionado a que los bienes sean incorporados a productos de exportación o retornados. "
                "Tipos: Controladora, Integradora, Industrial, Servicios, Albergue. "
                "Obligaciones: llevar sistema de control de inventarios en tiempo real (SECIIT), retornar o destruir la mercancía "
                "en los plazos autorizados (18 meses para insumos, 2 años para maquinaria). "
                "Incumplir convierte la importación temporal en definitiva, generando pago retroactivo de aranceles, IVA y recargos. "
                "El IMMEX se combina frecuentemente con el IVA Certificado para diferir el IVA de importaciones temporales."
            ),
            "topic": "immex",
            "fuente": "Decreto IMMEX 2006 (actualizado)",
        },
        {
            "title": "Agente aduanal: obligatoriedad y responsabilidades",
            "text": (
                "El agente aduanal es el profesional autorizado por el SAT/AGA para representar al importador o exportador ante "
                "la aduana. Su intervención es obligatoria cuando el valor de la mercancía excede el régimen de importación "
                "simplificada (USD 1,000) y para mercancías sujetas a regulaciones no arancelarias. "
                "Responsabilidades: clasificación arancelaria correcta, determinación y pago de contribuciones, declaración del "
                "valor en aduana, obtención de permisos previos. El agente responde solidariamente con el importador por "
                "contribuciones omitidas derivadas de su actuación. "
                "El apoderado aduanal es similar pero es empleado de la empresa; no puede actuar para terceros."
            ),
            "topic": "agente_aduanal",
            "fuente": "LA Arts. 159-163",
        },
        {
            "title": "Valoración aduanera: métodos y valor en aduana",
            "text": (
                "El valor en aduana es la base gravable para calcular el Impuesto General de Importación (IGI). "
                "Métodos en orden de prelación (Acuerdo de Valoración OMC): "
                "1) Valor de transacción — precio pagado o por pagar, más ajustes (comisiones, envases, royalties, seguros, flete). "
                "2) Valor de transacción de mercancías idénticas. "
                "3) Valor de transacción de mercancías similares. "
                "4) Valor deductivo — precio de venta en México menos márgenes. "
                "5) Valor reconstruido — costos de producción. "
                "6) Método residual — criterio razonable basado en métodos anteriores. "
                "El importador debe conservar la documentación que soporte el valor declarado por 5 años. "
                "La autoridad puede impugnar el valor si detecta inconsistencias con precios de mercado."
            ),
            "topic": "valoracion_aduanera",
            "fuente": "LA Arts. 64-78, Acuerdo OMC",
        },
        {
            "title": "NOMs aplicables al comercio exterior mexicano",
            "text": (
                "Las Normas Oficiales Mexicanas (NOMs) son regulaciones no arancelarias obligatorias para importaciones a México. "
                "El importador debe obtener el Certificado de Conformidad o la Constancia de Inspección del organismo acreditado "
                "antes del despacho aduanal. NOMs frecuentes en importación: "
                "NOM-024-SCFI (info comercial en productos eléctricos), NOM-050-SCFI (info comercial bienes de consumo), "
                "NOM-003-SSA1 (plaguicidas), NOM-015-SCFI (juguetes), NOM-041-SSA1 (etiquetado de medicamentos). "
                "Las NOMs deben indicarse en el pedimento. Importar sin cumplir NOM aplicable puede resultar en "
                "embargo precautorio de la mercancía y multa hasta el 10% del valor en aduana."
            ),
            "topic": "nom_comercio_exterior",
            "fuente": "LA Art. 36-A fracc. II, LFMN",
        },
    ],
}


# ─── Main ─────────────────────────────────────────────────────────────────────

def seed_collection(collection: str, docs: list[dict]) -> int:
    """Inserta todos los documentos de una colección. Retorna cantidad insertada."""
    inserted = 0
    for i, doc in enumerate(docs, 1):
        text = doc["text"]
        metadata = {k: v for k, v in doc.items() if k != "text"}
        print(f"  [{i}/{len(docs)}] {doc.get('title','')[:60]}...", end=" ", flush=True)
        try:
            result = upsert(collection, text, metadata)
            status = result.get("status", "ok")
            print(f"OK ({status})")
            inserted += 1
        except Exception as e:
            print(f"ERROR: {e}")
        # Pequeña pausa para no saturar Ollama
        if i < len(docs):
            time.sleep(0.5)
    return inserted


def main():
    parser = argparse.ArgumentParser(description="Seed colecciones escasas en Qdrant")
    parser.add_argument(
        "--collections",
        default=",".join(KNOWLEDGE.keys()),
        help="Colecciones a procesar (separadas por coma)",
    )
    args = parser.parse_args()

    target_cols = [c.strip() for c in args.collections.split(",")]

    print("=== Seed Qdrant — Colecciones Escasas ===\n")
    print(f"Colecciones objetivo: {', '.join(target_cols)}")
    print(f"Ollama: {OLLAMA_URL}  |  Qdrant: {QDRANT_URL}\n")

    # Verificar Qdrant
    try:
        req = urllib.request.Request(f"{QDRANT_URL}/healthz")
        with urllib.request.urlopen(req, timeout=5):
            pass
    except Exception as e:
        print(f"ERROR: Qdrant no accesible en {QDRANT_URL}: {e}")
        sys.exit(1)

    # Verificar Ollama / embed test
    print("Verificando embedding de prueba...")
    try:
        vec = embed("prueba de conexión")
        print(f"  Embedding OK — dimensiones: {len(vec)}\n")
    except Exception as e:
        print(f"ERROR: Ollama no accesible: {e}")
        sys.exit(1)

    results = {}
    total_inserted = 0

    for col in target_cols:
        if col not in KNOWLEDGE:
            print(f"[SKIP] {col} — no hay conocimiento definido para esta colección")
            continue

        docs = KNOWLEDGE[col]
        before = get_points_count(col)
        print(f"\n[{col}] {before} puntos existentes → agregando {len(docs)} documentos")
        inserted = seed_collection(col, docs)
        after = get_points_count(col)
        results[col] = {"antes": before, "insertados": inserted, "total": after}
        total_inserted += inserted

    # Resumen
    print("\n" + "=" * 50)
    print("RESUMEN FINAL")
    print("=" * 50)
    for col, r in results.items():
        print(f"  {col:<20} antes={r['antes']:>3}  +{r['insertados']}  total={r['total']:>3}")
    print(f"\n  TOTAL INSERTADOS: {total_inserted}")
    print("=" * 50)

    if total_inserted > 0:
        print("\nSeed completado exitosamente.")
    else:
        print("\nNingún documento fue insertado. Revisar logs.")


if __name__ == "__main__":
    main()
