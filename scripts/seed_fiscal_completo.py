#!/usr/bin/env python3
"""
seed_fiscal_completo.py — Seed masivo de Qdrant con conocimiento fiscal MX

Cubre: tipos de contadores, NIF A-D, SAT DOF 2024-2026, VUCEM,
importaciones/exportaciones, IMSS, declaraciones, leyes, regímenes.

Uso (en VPS):
    cd /home/mystic/sonora-digital-corp
    python3 scripts/seed_fiscal_completo.py
"""
import asyncio
import os
import sys

# ── Config ────────────────────────────────────────────────────────────────────

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "mystic_knowledge")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# ── Documentos ────────────────────────────────────────────────────────────────

DOCUMENTS = [
    # ════════════════════════════════════════════════════════════════════════
    # TIPOS DE CONTADORES EN MÉXICO
    # ════════════════════════════════════════════════════════════════════════
    {
        "title": "Contador Público (CP) — Perfil y funciones",
        "topic": "contadores",
        "content": """El Contador Público (CP) es el profesional con título universitario en Contaduría Pública
emitido por universidad reconocida por SEP. Sus funciones principales son:
- Elaboración y presentación de estados financieros (Balance General, Estado de Resultados, Flujo de Efectivo)
- Declaraciones fiscales: ISR anual personas físicas y morales, IVA mensual, IMSS patronal
- Contabilidad electrónica SAT (XML mensual, catálogo de cuentas COA)
- Nómina: cálculo ISR retenciones, IMSS cuotas obrero-patronal, INFONAVIT
- Facturación CFDI 4.0: emisión, recepción, cancelación, complementos
- Cumplimiento RESICO, RIF, Plataformas Digitales
Colegio más importante: IMCP (Instituto Mexicano de Contadores Públicos)
Certificación voluntaria: CPC (Contador Público Certificado) válida 3 años.""",
    },
    {
        "title": "Contador Público Certificado (CPC) — Requisitos y privilegios",
        "topic": "contadores",
        "content": """El CPC es la certificación más alta en México para contadores.
Otorgada por el IMCP (Instituto Mexicano de Contadores Públicos).
Requisitos: título de CP + 3 años experiencia + examen de certificación + educación continua.
Renovación cada 3 años con 120 horas de educación profesional continua (EPC).
Privilegios exclusivos:
- Dictámenes fiscales (SIPRED/DISIF) ante el SAT — solo CPC pueden emitirlos
- Dictamen IMSS (SIDEIMSS) — auditoría de cuotas patronales
- Informes de auditoría externa para empresas públicas
- Avalúos inmobiliarios con valor fiscal oficial
Examen: 4 módulos — Contabilidad, Fiscal, Auditoría, Finanzas. Mínimo 70/100 para aprobar.""",
    },
    {
        "title": "Auditor Fiscal — Funciones y tipos de auditoría SAT",
        "topic": "contadores",
        "content": """El Auditor Fiscal puede ser:
1. Auditor interno: empleado de la empresa que revisa controles y cumplimiento
2. Auditor externo: despacho independiente que emite dictamen
3. Auditor SAT: funcionario del SAT que ejecuta revisiones

Tipos de revisión del SAT:
- Visita domiciliaria: auditores van al negocio a revisar documentación
- Revisión de gabinete: contribuyente lleva papeles a oficinas SAT
- Revisión electrónica: solo vía buzón tributario, sin visita
- EFOS/EDOS: revisión de operaciones con empresas fantasma (art. 69-B CFF)
- Carta invitación: no es auditoría formal, solo sugerencia de corrección

Plazo máximo de revisión: 12 meses (18 para grandes contribuyentes, 2 años con delitos)
Derechos del contribuyente: acceso a expediente, impugnar con recurso de revocación o TFJA.""",
    },
    {
        "title": "Dictaminador Fiscal SIPRED — Quién puede dictaminar",
        "topic": "contadores",
        "content": """SIPRED = Sistema de Presentación del Dictamen Fiscal (SAT).
Solo CPCs registrados ante el SAT pueden emitir dictámenes.
Registro SIPRED: solicitud + pago derechos + certificado FIEL + vigencia anual.

Empresas obligadas a dictaminar (art. 32-A CFF):
- Ingresos > $1,650 millones de pesos en ejercicio anterior
- Acciones colocadas en bolsa de valores
- Residentes en el extranjero con establecimiento permanente
Voluntario: cualquier empresa puede optar por dictaminarse.

El dictamen SIPRED incluye:
- Balance general y estado de resultados auditados
- Relación de contribuciones pagadas (ISR, IVA, IMSS, INFONAVIT, etc.)
- Informe sobre la situación fiscal del contribuyente
Plazo de presentación: 15 de julio del ejercicio siguiente.""",
    },
    {
        "title": "Consultor Fiscal — Planeación y estructuras legales",
        "topic": "contadores",
        "content": """El Consultor Fiscal se especializa en planeación fiscal legal (no evasión).
Herramientas de planeación:
- Diferimiento de ingresos y aceleración de deducciones
- Estructuras holding (empresa tenedora + subsidiarias)
- Precios de transferencia (art. 179-184 LISR) para empresas con partes relacionadas
- Tratados para evitar doble tributación (México tiene 76 tratados activos)
- REFIPRE: Regímenes fiscales preferentes — declaración anual especial
- Trust y fideicomisos como herramientas de planeación patrimonial
- Opción personas morales: pago ISR sobre flujo (art. 196 LISR)

Riesgo: ESQUEMAS REPORTABLES (arts. 197-202 CFF) — consultor debe reportar esquemas al SAT.
Multa por no reportar: 15,000 a 20,000 UMAs diarias.""",
    },
    {
        "title": "Contador especialista en IMSS/INFONAVIT — Nómina avanzada",
        "topic": "contadores",
        "content": """Especialista en seguridad social y nómina. Funciones:
- Registro patronal IMSS: alta, modificaciones, baja
- SUA (Sistema Único de Autodeterminación): cálculo bimestral cuotas IMSS
- IDSE (IMSS Desde Su Empresa): movimientos afiliatorios en línea
- Subrogación y outsourcing: nuevas reglas 2021 — solo REPSE autorizados
- INFONAVIT: créditos hipotecarios, retenciones, amortizaciones, liquidaciones
- PTU (Participación de los Trabajadores en las Utilidades): cálculo art. 123 constitucional
- Prima de riesgo de trabajo: revisión anual IMSS, cálculo por siniestralidad

Tablas IMSS 2026:
- Salario mínimo: $278.80/día (área geográfica A)
- Salario mínimo zona libre frontera norte: $419.88/día
- UMA 2026: $113.14/día | $3,439.56/mes | $41,274.72/año
- Límite superior sueldo base cotización (SBC): 25 UMAs = $2,828.50/día""",
    },
    {
        "title": "Contador especialista en Comercio Exterior — Aduanas y VUCEM",
        "topic": "contadores",
        "content": """Especialidad en importaciones, exportaciones y cumplimiento aduanero.
Conocimientos requeridos:
- TIGIE (Tarifa del IEPS General de Importación y Exportación) — 98 capítulos
- Clasificación arancelaria: 10 dígitos, interpretación Reglas GATT
- Pedimento de importación: tipos A1 (definitiva), V1 (exportación definitiva), IT (importación temporal)
- VUCEM (Ventanilla Única de Comercio Exterior Mexicano): plataforma digital Sedecon
- IVA importación: 16% sobre valor en aduana + contribuciones
- DTA (Derecho de Trámite Aduanero): 8‰ del valor en aduana
- NOM verificación: etiquetas, normas técnicas, permisos previos SENASICA/COFEPRIS

Regímenes principales:
- Importación definitiva (clave A1)
- Exportación definitiva (clave V1)
- Maquila/IMMEX: temporal sin pago de impuestos + beneficio IVA 0%
- Recinto Fiscalizado Estratégico (RFE): almacenamiento sin pago hasta retiro""",
    },

    # ════════════════════════════════════════════════════════════════════════
    # NORMAS DE INFORMACIÓN FINANCIERA (NIF)
    # ════════════════════════════════════════════════════════════════════════
    {
        "title": "NIF Serie A — Marco conceptual (NIF A-1 a A-8)",
        "topic": "NIF",
        "content": """Las NIF Serie A son el marco conceptual base de la contabilidad mexicana.
NIF A-1: Estructura de las Normas de Información Financiera
NIF A-2: Postulados básicos — entidad económica, negocio en marcha, devengación, asociación de costos y gastos, valuación, dualidad económica, consistencia, revelación suficiente, importancia relativa, no compensación.
NIF A-3: Necesidades de los usuarios y objetivos de los estados financieros
NIF A-4: Características cualitativas — confiabilidad, relevancia, comprensibilidad, comparabilidad
NIF A-5: Elementos básicos de los estados financieros — activos, pasivos, capital, ingresos, costos y gastos, utilidad o pérdida
NIF A-6: Reconocimiento y valuación — costo histórico, valor razonable, valor neto de realización, valor presente, costo de reposición
NIF A-7: Presentación y revelación
NIF A-8: Supletoriedad (IFRS cuando no hay NIF mexicana aplicable)""",
    },
    {
        "title": "NIF Serie B — Estados Financieros (NIF B-1 a B-17)",
        "topic": "NIF",
        "content": """NIF Serie B regula la presentación de estados financieros.
NIF B-1: Cambios contables y correcciones de errores
NIF B-2: Estado de flujos de efectivo (método directo e indirecto)
NIF B-3: Estado de resultado integral
NIF B-4: Estado de cambios en el capital contable
NIF B-5: Información financiera por segmentos
NIF B-6: Estado de situación financiera (balance general)
NIF B-7: Adquisiciones de negocios
NIF B-8: Estados financieros consolidados y combinados
NIF B-9: Información financiera a fechas intermedias
NIF B-10: Efectos de la inflación (INPC, valor UDI)
NIF B-11: Disposición de activos de larga duración y operaciones discontinuadas
NIF B-12: Compensación de activos financieros y pasivos financieros
NIF B-13: Hechos posteriores a la fecha de los estados financieros
NIF B-14: Utilidad por acción
NIF B-15: Conversión de monedas extranjeras
NIF B-16: Estados financieros de entidades con propósito no lucrativo
NIF B-17: Determinación del valor razonable""",
    },
    {
        "title": "NIF Serie C — Normas aplicables a conceptos específicos",
        "topic": "NIF",
        "content": """NIF Serie C norma partidas específicas del Balance y Estado de Resultados.
NIF C-1: Efectivo y equivalentes de efectivo
NIF C-2: Inversión en instrumentos financieros (FVTPL, FVOCI, costo amortizado)
NIF C-3: Cuentas por cobrar (estimación cuentas incobrables, CECL modelo)
NIF C-4: Inventarios (PEPS, costo promedio — ya no UEPS en México)
NIF C-5: Pagos anticipados
NIF C-6: Propiedades, planta y equipo (depreciación, valor residual, deterioro)
NIF C-7: Inversiones en asociadas, negocios conjuntos y otras inversiones permanentes
NIF C-8: Activos intangibles (amortización, vida útil definida vs indefinida)
NIF C-9: Provisiones, contingencias y compromisos
NIF C-10: Instrumentos financieros derivados y operaciones de cobertura
NIF C-11: Capital contable
NIF C-12: Instrumentos financieros con características de pasivo y de capital
NIF C-13: Partes relacionadas (revelar, precio de mercado o justificado)
NIF C-14: Transferencia y baja de activos financieros
NIF C-15: Deterioro en el valor de los activos de larga duración y su disposición
NIF C-16: Deterioro de instrumentos financieros por cobrar
NIF C-17: Propiedades de inversión
NIF C-19: Instrumentos financieros por pagar
NIF C-20: Instrumentos financieros para cobrar principal e interés
NIF C-21: Acuerdos con control conjunto (Joint ventures)
NIF C-22: Criptomonedas (reconocimiento como activo intangible o inventario)""",
    },
    {
        "title": "NIF Serie D — Normas aplicables a problemas de determinación de resultados",
        "topic": "NIF",
        "content": """NIF Serie D para reconocimiento de ingresos, costos y beneficios.
NIF D-1: Ingresos por contratos con clientes (similar a IFRS 15)
  - 5 pasos: identificar contrato, obligaciones de desempeño, precio transacción, asignar precio, reconocer al cumplir
NIF D-2: Costos por contratos con clientes (costos de obtener y cumplir contratos)
NIF D-3: Beneficios a los empleados
  - Corto plazo: sueldos, PTU, vacaciones, aguinaldo
  - Largo plazo: prima de antigüedad (art. 162 LFT), pensiones, IMSS
  - Terminación: indemnizaciones 90 días + 20 días por año + partes proporcionales
NIF D-4: Impuestos a la utilidad (ISR diferido — diferencias temporales)
NIF D-5: Arrendamientos (similar a IFRS 16 — activo por derecho de uso + pasivo)
NIF D-6: Capitalización del resultado integral de financiamiento

Aguinaldo mínimo legal: 15 días de salario (art. 87 LFT), pagar antes 20 diciembre
Prima vacacional mínima: 25% sobre salario de días de vacaciones (art. 80 LFT)
PTU: 10% de utilidad fiscal ajustada, pagar antes 31 mayo personas morales, 30 junio personas físicas.""",
    },

    # ════════════════════════════════════════════════════════════════════════
    # SAT / ISR / IVA — REFORMAS 2024-2026
    # ════════════════════════════════════════════════════════════════════════
    {
        "title": "ISR Personas Morales 2026 — Tasa, pagos provisionales, anual",
        "topic": "SAT_fiscal",
        "content": """ISR (Impuesto Sobre la Renta) personas morales México 2026:
Tasa: 30% sobre utilidad fiscal (ingresos - deducciones autorizadas - PTU pagada)
Pagos provisionales: mensuales, los 17 de cada mes siguiente
  Cálculo: ingresos acumulados × coeficiente de utilidad (del ejercicio anterior)
  Coeficiente = utilidad fiscal / ingresos netos del ejercicio previo
Declaración anual: 31 de marzo del ejercicio siguiente (personas morales)
  31 de abril para personas físicas con actividad empresarial

Deducción inmediata de inversiones: activos fijos nuevos, primer año de uso.
ISR diferido: diferencias temporales activo (DTAs) — NIF D-4.
Consolidación fiscal: grupos de empresas con 80%+ propiedad pueden consolidar.

Cambio DOF 2025: eliminación deducción de intereses FIBRAS excesivos (anti-BEPS).
Cambio DOF 2026: retención ISR plataformas digitales — tasa fija 1% sobre monto total cobrado.""",
    },
    {
        "title": "IVA 2026 — Tasas, acreditamiento, declaración, retenciones",
        "topic": "SAT_fiscal",
        "content": """IVA (Impuesto al Valor Agregado) México 2026:
Tasa general: 16%
Tasa frontera norte (Zona Libre): 8% (municipios Tijuana, Mexicali, Nogales, Cd. Juárez, Matamoros, Nuevo Laredo, Reynosa, Cd. Acuña, Piedras Negras, Agua Prieta, Naco, Sonoyta, Puerto Peñasco)
Tasa 0%: alimentos no procesados, medicamentos, agua potable, exportaciones, libros, periódicos
Exentos: servicios educativos, transporte foráneo, seguros agropecuarios, intereses hipotecas casa habitación, arrendamiento casa habitación

Acreditamiento IVA: solo si cumple 4 requisitos: actividad gravada, pagado efectivamente, CFDI válido, deducible en ISR.
Retenciones IVA obligatorias:
- Personas morales a personas físicas: 2/3 del IVA (10.666%)
- Manobra de carga, descarga, comisión, mediación, agencia, representación: 4% del total
- Servicios de transporte de carga: 4%
- Plataformas digitales residentes en extranjero: 100% retención

Declaración: 17 de cada mes (art. 5-D LIVA). Saldo a favor: devolución o compensación.""",
    },
    {
        "title": "RESICO — Régimen Simplificado de Confianza 2022-2026",
        "topic": "SAT_fiscal",
        "content": """RESICO (Régimen Simplificado de Confianza) vigente desde enero 2022.
Para personas físicas con ingresos hasta $3.5 millones anuales.
Para personas morales con ingresos hasta $35 millones anuales.

Personas físicas RESICO:
- ISR: tabla progresiva 1% a 2.5% según ingresos (mucho menor que régimen general)
- IVA: sigue siendo 16% o 0% según actividad
- No requieren llevar contabilidad electrónica compleja
- Pagos mensuales definitivos (no provisionales)
- No presentan declaración anual ISR
- Incompatible con: ingresos por salarios (asalariados puros), actividades agrícolas RIF, socios de personas morales con >10% acciones

Personas morales RESICO:
- ISR: 30% sobre utilidades distribuidas (dividendos) — solo tributan cuando reparten
- Retención ISR dividendos: 10% adicional
- Deben emitir CFDI por todas las operaciones
- Contabilidad electrónica obligatoria (simplificada)""",
    },
    {
        "title": "Contabilidad Electrónica SAT — Catálogo de Cuentas y Balanza",
        "topic": "SAT_fiscal",
        "content": """La Contabilidad Electrónica SAT (CFF art. 28, RMF 2.8.1.3-2.8.1.9) requiere envío de:
1. Catálogo de Cuentas (COA): en enero + cuando haya cambios. Formato XML SAT.
   - Código SAT de 3 dígitos (grupo) + subcuentas propias de la empresa
   - 1xx Activo, 2xx Pasivo, 3xx Capital, 4xx Ingresos, 5xx Costos, 6xx Gastos, 7xx Otros
2. Balanza de Comprobación: mensual, los días 25-27 del mes siguiente
3. Pólizas de Contabilidad: solo si hay auditoría o compensación de IVA > $1 millón

Moneda funcional: peso mexicano. Si tienen operaciones en USD, convertir con tipo de cambio DOF del día.
Software reconocido SAT: CONTPAQi, Aspel COI, SIIGO, SAP, Oracle NetSuite.

Obligación nuevos contribuyentes: registro contable desde primer mes de operaciones.
Microempresas (ingresos < $4 millones): pueden llevar registro simplificado Excel.""",
    },
    {
        "title": "CFDI 4.0 — Obligaciones, cancelación, complementos 2026",
        "topic": "SAT_fiscal",
        "content": """CFDI 4.0 vigente desde 1 enero 2022 (obligatorio desde 1 enero 2023).
Cambios principales vs CFDI 3.3:
- Nombre y domicilio fiscal del receptor obligatorio (antes opcional)
- Uso del CFDI: código catálogo SAT obligatorio (G01 Adquisición de mercancias, G03 Gastos en general, D01 Honorarios médicos, I01 Construcciones, P01 Por definir, etc.)
- Régimen fiscal receptor obligatorio
- Exportación: campo obligatorio (01 No aplica, 02 Definitiva, 03 Temporal, 04 Retorno)
- Objecto de impuesto: 01 No objeto, 02 Sí objeto, 03 Sí objeto, no causa, 04 Sí objeto, no causa, no acreditable

Cancelación CFDI 4.0: requiere UUID, motivo (01 Comprobante emitido con errores con relación, 02 Comprobante emitido con errores sin relación, 03 No se llevó a cabo la operación, 04 Operación nominativa relacionada), y aceptación receptor si el monto > $1,000.

Complementos frecuentes: Nómina 1.2, Carta Porte 2.0 (transporte terrestre), Comercio Exterior 1.1, Pago 1.0/2.0, SPEI terceros, Leyendas Fiscales, Venta de Vehículos.""",
    },

    # ════════════════════════════════════════════════════════════════════════
    # VUCEM — VENTANILLA ÚNICA DE COMERCIO EXTERIOR
    # ════════════════════════════════════════════════════════════════════════
    {
        "title": "VUCEM — Qué es y cómo funciona para importaciones",
        "topic": "VUCEM",
        "content": """VUCEM (Ventanilla Única de Comercio Exterior Mexicano) es la plataforma digital de la SEDECON para gestionar permisos, licencias y certificados de comercio exterior.
URL oficial: vucem.gob.mx

Documentos que se gestionan en VUCEM:
- Permisos de importación automáticos y no automáticos (SEDECON)
- Certificados fitosanitarios (SENASICA/SADER) para productos agropecuarios
- Avisos de COFEPRIS para medicamentos, alimentos procesados, cosméticos
- Permisos de la Secretaría de Salud (SS) para productos controlados
- Dictamen NOM: verifica que producto cumple con normas técnicas mexicanas
- Licencias SENER para petrolíferos, gas LP, energía eléctrica
- Certificado de origen para aprovechar tratados (T-MEC, TLCUEM, etc.)

Proceso de importación con VUCEM:
1. Solicitar permiso/aviso previo en VUCEM con FIEL
2. VUCEM genera folio y número de documento
3. Agente aduanal captura folio en pedimento
4. Aduana verifica electrónicamente en VUCEM
5. Mercancía liberada si todo coincide""",
    },
    {
        "title": "VUCEM — Pedimento de importación definitiva (A1)",
        "topic": "VUCEM",
        "content": """Pedimento A1 = Importación Definitiva de mercancías al territorio nacional.
Elementos del pedimento:
- RFC importador + nombre/razón social
- Aduana de entrada (Nogales, Tijuana, Manzanillo, Veracruz, AICM, etc.)
- Fracción arancelaria (10 dígitos TIGIE)
- Descripción de mercancía, cantidad, unidad de medida
- País de origen + procedencia
- Valor en aduana (USD o moneda extranjera convertida a MXN)
- Contribuciones: IGI (arancel) + DTA + IVA importación + IEPS si aplica
- Régimen aduanero: A1 definitiva
- Número de pedimento (anual/agencia/secuencia)

Cálculo de contribuciones:
1. Valor en aduana = precio pagado + seguro + flete hasta aduana MX
2. IGI = valor aduana × tasa arancelaria (TIGIE, considera TLC)
3. DTA = MAX(valor aduana × 8‰, cuota mínima)
4. Precio oficial base IVA = valor aduana + IGI + DTA + IEPS
5. IVA importación = precio oficial base × 16%

Documentos anexos: factura comercial, lista de empaque (packing list), conocimiento de embarque (BL/AWB), certificado de origen si hay TLC.""",
    },
    {
        "title": "T-MEC (USMCA) — Reglas de origen y ventajas arancelarias",
        "topic": "VUCEM",
        "content": """T-MEC (Tratado México-Estados Unidos-Canadá) vigente desde 1 julio 2020.
Sustituyó al TLCAN/NAFTA. Cubre casi la totalidad del comercio trilateral.

Para aprovechar arancel 0% o preferencial:
1. Mercancía debe cumplir regla de origen T-MEC
2. Tres criterios de origen: a) Enteramente producida en región, b) Cambio de clasificación arancelaria, c) Contenido de valor regional (CVR) mínimo
3. Certificación de origen: desde T-MEC ya no hay formulario oficial — puede ser en factura o documento separado, firmado por exportador, productor o importador

Sectores con reglas especiales T-MEC:
- Automotriz: CVR mínimo 75% (fase 4 2023+) con partes de acero/aluminio N.A.
- Textil: yarn-forward (fibra en región)
- Productos agrícolas: reglas específicas por producto

Ventajas digitales: certificación electrónica, integración VUCEM-USTR, auditorías cruzadas USA-MX.
Cuota de salvaguarda azúcar: 1,025,000 toneladas libres de arancel (excedente paga arancel).""",
    },
    {
        "title": "IMMEX — Maquiladoras e importación temporal",
        "topic": "VUCEM",
        "content": """IMMEX (Industria Manufacturera, Maquiladora y de Servicios de Exportación).
Decreto publicado DOF 1 noviembre 2006, múltiples reformas.

Beneficios IMMEX:
- Importación temporal de insumos, maquinaria, equipo sin pago de IGI, DTA ni IVA
- Plazo: 18 meses materia prima / 24 meses contenedores / hasta 10 años activos fijos
- Retorno: 100% de mercancía importada temporalmente debe retornarse o cambiarse a régimen definitivo

Requisitos para obtener IMMEX:
- Exportar mínimo USD 500,000 anuales o 10% de facturación
- No tener créditos fiscales exigibles
- Estar al corriente de declaraciones SAT e IMSS
- Inscribirse en el Padrón de Importadores

IVA en IMMEX: certificación IVA-IEPS permite acreditar IVA de importación temporal sin pagar (depósito en garantía automático).

VUCEM integrado: todos los pedimentos temporales de IMMEX usan folio VUCEM para control de inventario.""",
    },

    # ════════════════════════════════════════════════════════════════════════
    # SAT — CALENDARIO FISCAL 2026
    # ════════════════════════════════════════════════════════════════════════
    {
        "title": "Calendario SAT 2026 — Fechas límite declaraciones personas morales",
        "topic": "calendario_SAT",
        "content": """Fechas límite declaraciones personas morales (régimen general) México 2026:

MENSUALES (vencen día 17 del mes siguiente):
- IVA: declaración + pago el 17 de cada mes
- ISR provisional: el 17 de cada mes
- IEPS: el 17 de cada mes (si aplica)
- Retenciones ISR: sueldos, honorarios, arrendamiento, dividendos — el 17

BIMESTRALES (personas físicas RESICO, RIF):
- 17 de marzo (ene-feb), 17 de mayo (mar-abr), 17 de julio (may-jun),
  17 de septiembre (jul-ago), 17 de noviembre (sep-oct), 17 de enero 2027 (nov-dic)

ANUALES 2026:
- Personas morales ISR anual: 31 de marzo 2027
- Personas físicas ISR anual: 30 de abril 2027
- Declaración informativa de operaciones con terceros (DIOT): 17 de cada mes
- DISIF/SIPRED: 15 de julio 2027

ESPECIALES 2026:
- PTU personas morales: pagar antes 31 mayo 2026
- PTU personas físicas: pagar antes 30 junio 2026
- Prima vacacional: aniversario de cada trabajador
- Aguinaldo: pagar antes 20 diciembre 2026""",
    },
    {
        "title": "DIOT — Declaración Informativa de Operaciones con Terceros",
        "topic": "calendario_SAT",
        "content": """DIOT (Declaración Informativa de Operaciones con Terceros) — Formato A-29.
Obligatoria para personas morales y físicas con actividad empresarial.
Plazo: los 17 de cada mes (información del mes anterior).

Qué reporta el DIOT:
- RFC de cada proveedor con quien se tuvo operación en el mes
- Monto total de operaciones (sin IVA)
- IVA pagado a la tasa de 16%
- IVA pagado a la tasa de 0%
- IVA exento
- IVA retenido (si aplica — cuando se paga a persona física)
- Tipo de operación: 03 Prestación de servicios profesionales, 06 Arrendamiento, 85 Importación de servicios, 85 Demás

Formato DIOT: archivo de texto (.txt) con campos separados por pipes (|).
Software: DIOT Lite, Aspel SAE, CONTPAQi Comercial.
Proveedores nacionales: requieren RFC válido.
Proveedores extranjeros: se reporta como "XEXX010101000" y país.
Penalización: no presentar DIOT = multa $3,030 a $30,410 MXN por período omitido.""",
    },

    # ════════════════════════════════════════════════════════════════════════
    # IMPORTACIONES Y EXPORTACIONES
    # ════════════════════════════════════════════════════════════════════════
    {
        "title": "Fracciones arancelarias TIGIE — Capítulos más comunes MX",
        "topic": "aduanas",
        "content": """TIGIE (Tarifa del IEPS General de Importación y Exportación) — 98 capítulos.
Estructura: 2 dígitos capítulo + 4 dígitos partida + 2 subpartida + 2 fracción MX = 10 dígitos

Capítulos más utilizados en importaciones MX:
- Cap. 84: Reactores nucleares, calderas, máquinas, aparatos mecánicos
  Ej: 8481.80.19 — Válvulas para fluidos industriales (filtración)
- Cap. 85: Máquinas eléctricas, equipos electrónicos
  Ej: 8544.42.99 — Cables y conductores eléctricos
- Cap. 87: Vehículos automóviles, tractores, bicicletas
  Ej: 8708.99.99 — Partes de vehículos n.e.p.
- Cap. 39: Plásticos y manufacturas de plástico
  Ej: 3926.90.99 — Manufacturas de plástico n.e.p.
- Cap. 73: Manufacturas de hierro o acero
  Ej: 7307.99.99 — Accesorios de tubería de acero
- Cap. 90: Instrumentos ópticos, médicos, de precisión
  Ej: 9026.80.99 — Instrumentos medición de líquidos y gases

Búsqueda oficial: www.ventanillaunica.gob.mx/vucem/Consultas.html
Clasificación arancelaria: servicio pagado, tarda 3-15 días hábiles en SEDECON.""",
    },
    {
        "title": "Incoterms 2020 — Reglas internacionales de comercio",
        "topic": "aduanas",
        "content": """Incoterms 2020 (International Commercial Terms) — ICC Paris.
Define quién paga qué en el transporte internacional.

GRUPO E (Salida):
- EXW (Ex Works): Comprador paga TUTTO desde fábrica vendedor

GRUPO F (Flete no pagado):
- FCA (Free Carrier): vendedor entrega en lugar convenido, sin flete internacional
- FAS (Free Alongside Ship): vendedor lleva hasta muelle
- FOB (Free On Board): vendedor carga en barco — más usado en importaciones MX

GRUPO C (Flete pagado):
- CFR (Cost and Freight): vendedor paga flete, comprador paga seguro
- CIF (Cost Insurance Freight): vendedor paga flete + seguro — base valor en aduana MX
- CPT (Carriage Paid To): como CFR para cualquier modo transporte
- CIP (Carriage Insurance Paid): como CIF para cualquier modo

GRUPO D (Destino):
- DAP (Delivered at Place): vendedor entrega en destino sin desaduanar
- DPU (Delivered at Place Unloaded): idem + descarga
- DDP (Delivered Duty Paid): vendedor paga TODO incluyendo impuestos destino

Para aduana MX: valor en aduana = CIF (si es marítimo) o CIP (si es aéreo/terrestre).""",
    },
    {
        "title": "Agente Aduanal — Rol, responsabilidades y padrón de importadores",
        "topic": "aduanas",
        "content": """El Agente Aduanal es el único facultado para despachar mercancías ante la aduana.
Patente aduanal: otorgada por SHCP, intransferible.
Responsabilidad solidaria: comparte responsabilidad fiscal con importador.

Padrón de Importadores (SAT):
- Toda empresa que importe regularmente debe inscribirse
- Requisitos: RFC activo, FIEL, domicilio fiscal verificable, no tener créditos exigibles
- Padrón Sectorial: para productos sensibles (acero, textil, zapato, químicos, etc.)
- Suspensión del padrón: importador suspendido no puede importar hasta regularizarse

Proceso típico de importación MX:
1. Empresa negocia con proveedor exterior (factura comercial en USD)
2. Solicitar VUCEM: permisos previos si aplica
3. Agente aduanal clasifica fracción + calcula contribuciones
4. Prepaga contribuciones vía banco (transferencia electrónica a cuenta SAT)
5. Presenta pedimento digital en sistema SAAI M3
6. Aduana: semáforo verde (paso libre) o rojo (reconocimiento físico)
7. Mercancía liberada + entrega

Tiempos promedio aduana MX: Nogales 4-8 horas, Manzanillo 24-72 horas, AICM 2-6 horas.""",
    },

    # ════════════════════════════════════════════════════════════════════════
    # IMSS AVANZADO
    # ════════════════════════════════════════════════════════════════════════
    {
        "title": "IMSS Cuotas Patronales 2026 — Cálculo detallado",
        "topic": "IMSS",
        "content": """Cuotas IMSS 2026 — Seguros y porcentajes sobre SBC:

ENFERMEDAD Y MATERNIDAD (EM):
- Prestaciones en especie (cuota fija): 20.40% SBC hasta 3 SMGDF = 4.04%
- Prestaciones en especie (excedente): 1.10% del excedente de 3 SMGDF
- Prestaciones en dinero patronal: 0.70%
- Prestaciones en dinero obrero: 0.25%
- Gastos médicos pensionados patronal: 1.05%

INVALIDEZ Y VIDA (IV): Patronal 1.75% + Obrero 0.625%
RETIRO (RT): Solo patronal 2.00%
CESANTÍA Y VEJEZ (CV): Patronal 3.150% + Obrero 1.125%
GUARDERÍAS (GY): Solo patronal 1.00%
INFONAVIT: Solo patronal 5.00%

Prima de riesgo de trabajo: varía por empresa (0.50% mínimo, hasta 15% clase V)

Ejemplo cálculo empleado SBC = $500/día:
- EM cuota fija: $500 × 4.04% = $20.20/día
- IV patronal: $500 × 1.75% = $8.75/día
- RT patronal: $500 × 2.00% = $10.00/día
- Total patronal: ≈ $150/día = $4,500/mes por empleado
- INFONAVIT: $500 × 5% = $25/día = $750/mes""",
    },
    {
        "title": "IMSS — Afiliación, movimientos y SUA 2026",
        "topic": "IMSS",
        "content": """SUA (Sistema Único de Autodeterminación) — software IMSS para cálculo de cuotas.
Descarga gratuita: imss.gob.mx/patrones

Movimientos afiliatorios IDSE (IMSS Desde su Empresa):
- Alta: antes de inicio de labores (o el mismo día)
- Baja: dentro de 5 días hábiles del fin de relación laboral
- Modificación de salario: dentro de 5 días hábiles del cambio
- Ausentismo e incapacidades: reportar antes del 3er día de incapacidad

Tipos de incapacidad:
- ST (Subsidio por enfermedad general): IMSS paga 60% del SBC desde día 4
- RT (Riesgo de trabajo): IMSS paga 100% desde día 1
- M (Maternidad): 100% SBC por 84 días (12 semanas antes + 6 después)

Pensión IMSS — Ley 97 (nacidos después 1997):
- Cuenta individual AFORE (Sistema de Ahorro para el Retiro)
- Cuota social IMSS: aportación fija por cotizante
- Requisito pensión: 1,250 semanas cotizadas + 60 años (vejez) o 65 (cesantía)
- Ley 73 (antes 1997): 500 semanas + edad + salario promedio últimas 250 semanas""",
    },

    # ════════════════════════════════════════════════════════════════════════
    # DECLARACIONES SAT — TODOS LOS TIPOS
    # ════════════════════════════════════════════════════════════════════════
    {
        "title": "Tipos de declaraciones SAT — Personas Morales México 2026",
        "topic": "declaraciones",
        "content": """Declaraciones que debe presentar una persona moral general:

MENSUALES:
1. ISR provisional (pago provisional mensual) — formato: declaración en portal SAT
2. IVA mensual definitivo — portal SAT
3. IEPS mensual — si comercializa bebidas alcohólicas, tabacos, gasolinas, etc.
4. Retenciones ISR: sueldos (art. 96), honorarios (art. 106), arrendamiento (art. 116), dividendos (art. 140)
5. Retenciones IVA (cuando aplica — pago a personas físicas)
6. DIOT (Declaración Informativa de Operaciones con Terceros)
7. Contabilidad electrónica: balanza de comprobación

TRIMESTRALES:
8. IVA personas físicas con actividad empresarial RESICO

ANUALES:
9. ISR anual (31 marzo)
10. Declaración informativa de partes relacionadas (DIM — Formas 55, 56)
11. DISIF/SIPRED (si obligado a dictaminar — 15 julio)
12. Declaración de préstamos a accionistas (si aplica)
13. Declaración informativa de operaciones > $100,000 en efectivo

EVENTUALES:
14. Aviso cambio de domicilio fiscal
15. Aviso de apertura/cierre de establecimientos
16. Declaración complementaria (corrección de errores)
17. Aviso de destrucción de mercancías (deducción de mermas)""",
    },
    {
        "title": "Tipos de declaraciones SAT — Personas Físicas México 2026",
        "topic": "declaraciones",
        "content": """Declaraciones personas físicas según régimen fiscal:

ASALARIADOS (Sueldos y Salarios):
- Solo si tienen otras fuentes de ingreso o si retención no fue suficiente
- Declaración anual: 30 de abril (puede generar saldo a favor = devolución automática)

HONORARIOS (Actividades Profesionales):
- ISR mensual: día 17 + IVA mensual: día 17 + DIOT: día 17
- ISR retención 10% si cliente es PM que retiene
- Declaración anual: 30 de abril

ARRENDAMIENTO:
- Opción 1: Deducción ciega 35% (sin comprobar gastos) + ISR mensual día 17
- Opción 2: Gastos comprobados + ISR mensual
- Declaración anual: 30 de abril

RESICO (hasta $3.5 millones):
- Pagos mensuales definitivos (no anuales): tasas 1% a 2.5%
- No presenta declaración anual ISR
- Sí presenta DIOT mensual
- Sí emite CFDI por cada operación

PLATAFORMAS DIGITALES (Uber, Rappi, Airbnb):
- Plataforma retiene ISR + IVA
- Si ingresos < $300,000/año: retención es pago definitivo (no declaración anual)
- Si ingresos > $300,000/año: declaración normal actividad empresarial

RÉGIMEN DE ACTIVIDADES EMPRESARIALES GENERAL:
- ISR provisional mensual + IVA + DIOT + Declaración anual 30 abril""",
    },

    # ════════════════════════════════════════════════════════════════════════
    # DOF — DISPOSICIONES RELEVANTES 2025-2026
    # ════════════════════════════════════════════════════════════════════════
    {
        "title": "DOF 2025 — Reformas fiscales principales publicadas",
        "topic": "DOF",
        "content": """Principales reformas fiscales DOF 2025 (publicadas y vigentes):

1. REFORMA ANTI-OUTSOURCING (CFF art. 26) — Actualización 2025:
   - REPSE: Registro de Prestadoras de Servicios Especializados u Obras Especializadas
   - Empresas que contraten servicios especializados deben verificar REPSE del prestador
   - Retención IVA 6% sobre servicios especializados (no el 100% anterior)
   - Penalización por no verificar: responsabilidad solidaria del contratante

2. FACTURA GLOBAL RESICO — Obligación ampliada:
   - Factura global mensual para ventas a público en general < $100 cada una
   - Desglose: cantidad de operaciones + montos por turno/día/semana/mes
   - RFC genérico: XAXX010101000

3. BUZÓN TRIBUTARIO OBLIGATORIO:
   - Todas las personas morales deben tener buzón activo con correo electrónico registrado
   - SAT puede notificar ahí con efectos legales plenos
   - No activar buzón: multa $3,030 a $9,080 MXN

4. COMPLEMENTO CARTA PORTE 3.0 — Vigente desde 2025:
   - Obligatorio para transporte terrestre de mercancías entre estados
   - Incluye: autotransporte, ferroviario, aéreo, marítimo
   - Sin carta porte: mercancía decomisada en revisión SAT""",
    },
    {
        "title": "DOF 2026 — Disposiciones fiscales nuevas enero-marzo",
        "topic": "DOF",
        "content": """Novedades DOF publicadas enero-marzo 2026:

1. RESOLUCIÓN MISCELÁNEA FISCAL 2026 (RMF 2026):
   Publicada 29 diciembre 2025 en DOF. Cambios relevantes:
   - Regla 2.1.37: nuevos CFDI para venta de divisas
   - Regla 3.13.1: RESICO — personas físicas con ingresos de copropiedad
   - Regla 4.1.5: IVA devoluciones automáticas hasta $1 millón en 5 días hábiles
   - Anexo 7: actualización catálogo usos CFDI (nuevos códigos S01, S02)
   - Anexo 24: actualización catálogo cuentas contabilidad electrónica

2. TASAS DE RETENCIÓN PLATAFORMAS DIGITALES 2026:
   - Transporte (Uber, Didi, Beat): 2.1% ISR + 8% IVA sobre ingreso bruto
   - Hospedaje (Airbnb, Vrbo): 4% ISR + 16% IVA
   - Venta de bienes (MercadoLibre, Amazon MX): 0.4% ISR + 8% IVA

3. NUEVA UMA 2026: $113.14 diario ($3,439.56 mensual, $41,274.72 anual)
   Impacto: topes cotización IMSS, multas CFF, aportaciones voluntarias AFORE

4. SALARIO MÍNIMO 2026: $278.80/día (área A) — incremento 12% vs 2025
   Zona libre frontera norte: $419.88/día (incremento 12%)""",
    },

    # ════════════════════════════════════════════════════════════════════════
    # CIERRE MENSUAL Y PROCEDIMIENTOS CONTABLES
    # ════════════════════════════════════════════════════════════════════════
    {
        "title": "Cierre Mensual Contable — Procedimiento paso a paso",
        "topic": "cierre",
        "content": """Procedimiento de cierre mensual para empresa PYME México:

SEMANA 1 DEL MES SIGUIENTE:
1. Conciliar cuentas bancarias: saldo libro vs estado de cuenta banco
2. Revisar CFDI emitidos vs registros contables (SAT vs sistema)
3. Registrar facturas de gastos del mes (CFDI recibidos)
4. Calcular depreciaciones de activos fijos (tarjeta de activos)
5. Provisionar nómina devengada (si el mes no coincide con fecha de pago)

SEMANA 2:
6. Presentar declaración ISR provisional (antes del 17)
7. Presentar declaración IVA (antes del 17)
8. Presentar DIOT (antes del 17)
9. Calcular y pagar cuotas IMSS con SUA (pago bimestral — enero, marzo, mayo, julio, septiembre, noviembre)
10. Generar balanza de comprobación SAT (enviar antes del 27)

CONCILIACIONES CLAVE:
- IVA trasladado en CFDI emitidos = IVA en declaración IVA
- Nómina contabilizada = recibos nómina CFDI emitidos = declaración IMSS
- Facturas de gastos = IVA acreditable declarado = DIOT reportado
- Bancos: chequera, tarjeta, transferencias = mayor contable

KPIs de salud para cierre:
- Margen bruto = (Ventas - Costo) / Ventas × 100
- Rotación de cartera = Ventas / Cuentas por cobrar promedio
- Días de pago = Cuentas por pagar / (Costo / 30)""",
    },

    # ════════════════════════════════════════════════════════════════════════
    # LEYES PRINCIPALES
    # ════════════════════════════════════════════════════════════════════════
    {
        "title": "CFF — Código Fiscal de la Federación: artículos clave",
        "topic": "leyes",
        "content": """Artículos más relevantes del CFF (Código Fiscal de la Federación) 2026:

Art. 1-A: Retenciones IVA — quién está obligado a retener
Art. 2: Crédito fiscal — definición
Art. 9: Personas morales residentes en México
Art. 12: Días hábiles para cómputo de plazos
Art. 14: Enajenación de bienes — concepto fiscal amplio
Art. 16: Actividades empresariales
Art. 17-D: FIEL (Firma Electrónica Avanzada) — requisitos y uso
Art. 26: Responsabilidad solidaria — administradores, socios, outsourcing
Art. 28: Contabilidad fiscal — libros, registros, conservación (5 años)
Art. 29: Comprobantes fiscales — CFDI obligatorio
Art. 31: Declaraciones — medios electrónicos
Art. 32: Modificación de declaraciones — complementarias, 3 años plazo
Art. 42: Facultades de comprobación SAT (auditoría, revisión)
Art. 46-A: Plazos de auditoría (12-18 meses)
Art. 52-A: Dictamen fiscal — requisitos
Art. 66-A: Autorización de facilidades de pago
Art. 69-B: EFOS (Empresas que Facturan Operaciones Simuladas) — proceso de notificación
Art. 108: Delito de defraudación fiscal — prisión 3 meses a 9 años según monto
Art. 197-202: Esquemas reportables — obligación de revelar planeaciones""",
    },
    {
        "title": "LISR — Ley del ISR artículos principales 2026",
        "topic": "leyes",
        "content": """Ley del Impuesto Sobre la Renta (LISR) — artículos clave 2026:

PERSONAS MORALES (Título II):
Art. 1: Sujetos del ISR — residentes en MX por ingresos mundiales
Art. 9: Tasa 30% personas morales
Art. 10: Utilidad fiscal = ingresos - deducciones - PTU pagada
Art. 14: Pagos provisionales mensuales (fórmula coeficiente utilidad)
Art. 16-17: Acumulación de ingresos — regla del devengado o cobrado
Art. 25-27: Deducciones autorizadas y prohibidas
Art. 31: Activos fijos — porcentajes de depreciación fiscal
Art. 32: Límite deducción gastos con automóviles ($0.93/km o $170,000 monto)
Art. 47-63: Reglas especiales industrias (financiero, seguros, agropecuario)
Art. 76: Obligaciones personas morales (contabilidad, declaraciones, CFDI)
Art. 140: Dividendos — retención 10% ISR adicional

PERSONAS FÍSICAS (Título IV):
Art. 90: Sujetos del ISR personas físicas
Art. 96: Retención ISR por salarios — tabla tarifas
Art. 106: Actividades profesionales — pagos provisionales 10%
Art. 114: Gastos deducibles honorarios: mínimo = el mayor de 5 SMAG o 8% ingresos
Art. 151: Deducciones personales: honorarios médicos, hospitales, colegiaturas (con tope)
Art. 152: Tarifa anual ISR — tasa marginal hasta 35%

RESICO (Título VII, Cap. XII-bis):
Art. 113-E: RESICO personas físicas — tasas 1% a 2.5%
Art. 206-212: RESICO personas morales — tributación sobre distribución""",
    },
    {
        "title": "LIVA — Ley del IVA: acreditamiento, retenciones, devoluciones",
        "topic": "leyes",
        "content": """Ley del Impuesto al Valor Agregado (LIVA) — artículos clave 2026:

Art. 1: Tasa 16%, sujetos (PM y PF con actividad empresarial)
Art. 2-A: Tasa 0% — alimentos no procesados, medicamentos, agua potable, exportaciones
Art. 3: Tasa 8% zona frontera norte
Art. 4: Concepto de acreditamiento — requisitos de los 4 (art. 5 LIVA)
Art. 5: Requisitos del acreditamiento:
  I. Que el gasto sea deducible para ISR
  II. Que esté trasladado por separado en CFDI
  III. Que esté efectivamente pagado (si es efectivo — inmediato; si crédito — hasta que se pague)
  IV. Que sea para actividades gravadas
Art. 5-A: Prorrateo IVA — cuando hay actividades mixtas (gravadas + exentas)
Art. 5-D: Declaración mensual definitiva
Art. 6: Saldo a favor IVA — derecho a devolución o compensación
Art. 7: Devoluciones de bienes — ajuste al IVA
Art. 14: Prestación de servicios — definición amplia
Art. 19: Traslado del IVA — requisitos del CFDI
Art. 1-A: Retenciones IVA obligatorias:
  I. Personas morales a personas físicas (honorarios, arrendamiento) — 2/3
  II. Personas morales a personas físicas (comisión, transporte) — 4%
  III. Residentes extranjero con establecimiento permanente — 100%""",
    },

    # ════════════════════════════════════════════════════════════════════════
    # MYSTIC — CASOS DE USO ESPECÍFICOS
    # ════════════════════════════════════════════════════════════════════════
    {
        "title": "Filtración industrial — Clasificación arancelaria y pedimentos",
        "topic": "aduanas",
        "content": """Productos de filtración industrial: fracciones arancelarias más usadas.

FILTROS Y ELEMENTOS FILTRANTES:
- 8421.21.01 — Aparatos para filtrar o depurar agua (doméstico)
- 8421.21.99 — Demás aparatos para filtrar o depurar agua (industrial)
- 8421.23.01 — Filtros de aceite para motor de combustión interna
- 8421.29.99 — Demás aparatos para filtrar o depurar líquidos
- 8421.39.99 — Demás aparatos para filtrar o depurar gases

MANGUERAS Y CONEXIONES:
- 3917.32.99 — Tubos rígidos de plástico n.e.p.
- 3917.39.99 — Tubos flexibles de plástico n.e.p.
- 7307.99.99 — Accesorios de tubería de acero inoxidable

BOMBAS Y SISTEMAS:
- 8413.60.99 — Demás bombas para líquidos (centrífugas)
- 8413.81.99 — Demás bombas volumétricas
- 8481.80.19 — Válvulas de control industrial (filtración)

Empresa Fourgea Mexico (RFC FME080820LC2): importa filtros industriales.
Pedimento referencia 26-23-3680-6000156 — fracción 8421.29.99
IGI aplicable: T-MEC 0% si origen USA/Canadá con certificación.
Si origen China/Europa: arancel TIGIE (generalmente 5-15% para filtros).""",
    },
    {
        "title": "Régimen General de Personas Morales — Obligaciones completas PYME",
        "topic": "SAT_fiscal",
        "content": """Checklist obligaciones fiscales PYME persona moral régimen general 2026:

MENSUAL (antes del 17):
✓ ISR provisional (coeficiente utilidad × ingresos acumulados)
✓ IVA declaración mensual
✓ DIOT (proveedores del mes)
✓ Retenciones ISR: nómina, honorarios, arrendamiento
✓ Retenciones IVA (si aplica)
✓ Balanza de comprobación SAT (antes del 25-27)
✓ Cuotas IMSS-SUA (bimestral: ene, mar, may, jul, sep, nov)
✓ Liquidación INFONAVIT (bimestral mismos meses)

TRIMESTRAL:
✓ Pago de luz CFE (aportar IVA/retenciones si aplica)

ANUAL (antes del 31 de marzo):
✓ ISR anual — conciliar provisionales vs utilidad real
✓ Declaración informativa DIM (partes relacionadas, préstamos, dividendos)
✓ Declaración enajenación de acciones (si hubo)
✓ PTU: calcular y pagar antes del 31 mayo

REGISTRO Y AVISOS:
✓ RFC activo + datos actualizados SAT
✓ FIEL/e.firma vigente (5 años, renovar antes de vencer)
✓ Buzón tributario activo con correo registrado
✓ Contabilidad electrónica actualizada (catálogo + balanza)
✓ Padrón importadores activo (si importa)
✓ REPSE activo (si presta o contrata servicios especializados)""",
    },
]


# ── Motor de embedding + Qdrant ───────────────────────────────────────────────

async def embed_text(text: str) -> list[float]:
    """Genera embedding con nomic-embed-text via Ollama."""
    import urllib.request as _req
    import json

    payload = json.dumps({"model": EMBED_MODEL, "prompt": text}).encode()
    request = _req.Request(
        f"{OLLAMA_URL}/api/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with _req.urlopen(request, timeout=30) as resp:
        data = json.loads(resp.read())
        return data["embedding"]


async def upsert_to_qdrant(collection: str, doc_id: int, vector: list[float], payload: dict):
    """Inserta un vector en Qdrant."""
    import urllib.request as _req
    import json

    body = json.dumps({
        "points": [{
            "id": doc_id,
            "vector": vector,
            "payload": payload
        }]
    }).encode()
    request = _req.Request(
        f"{QDRANT_URL}/collections/{collection}/points",
        data=body,
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    with _req.urlopen(request, timeout=10) as resp:
        return json.loads(resp.read())


async def ensure_collection(collection: str, vector_size: int = 768):
    """Crea la colección si no existe."""
    import urllib.request as _req
    import json

    # Verificar si existe
    try:
        req = _req.Request(f"{QDRANT_URL}/collections/{collection}")
        with _req.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            if data.get("result"):
                print(f"  Colección '{collection}' ya existe.")
                return
    except Exception:
        pass

    # Crear
    body = json.dumps({
        "vectors": {"size": vector_size, "distance": "Cosine"}
    }).encode()
    req = _req.Request(
        f"{QDRANT_URL}/collections/{collection}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    with _req.urlopen(req, timeout=10) as r:
        print(f"  Colección '{collection}' creada: {json.loads(r.read())}")


async def seed():
    print(f"\n{'='*60}")
    print(f"MYSTIC Seed Fiscal Completo — {len(DOCUMENTS)} documentos")
    print(f"Qdrant: {QDRANT_URL} | Colección: {QDRANT_COLLECTION}")
    print(f"Modelo embedding: {EMBED_MODEL}")
    print(f"{'='*60}\n")

    await ensure_collection(QDRANT_COLLECTION)

    ok = 0
    errors = 0
    for i, doc in enumerate(DOCUMENTS):
        title = doc["title"]
        topic = doc["topic"]
        content = doc["content"]

        try:
            # Combinar título + contenido para embedding más rico
            text_to_embed = f"{title}\n\n{content}"
            vector = await embed_text(text_to_embed)

            payload = {
                "title": title,
                "topic": topic,
                "content": content,
                "source": "seed_fiscal_completo",
                "lang": "es",
            }

            # ID único basado en posición + offset para no colisionar con seeds anteriores
            doc_id = 10000 + i

            await upsert_to_qdrant(QDRANT_COLLECTION, doc_id, vector, payload)
            ok += 1
            print(f"  [{i+1:02d}/{len(DOCUMENTS)}] OK — {title[:60]}")
        except Exception as e:
            errors += 1
            print(f"  [{i+1:02d}/{len(DOCUMENTS)}] ERROR — {title[:50]}: {e}")

    print(f"\n{'='*60}")
    print(f"COMPLETADO: {ok} OK | {errors} errores")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(seed())
