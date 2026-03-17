"""
seed_knowledge.py — Base de Conocimiento Fiscal Mexicano
Carga conocimiento verificado para el Brain IA (RAG)

Cobertura:
  A. ISR — Personas Morales y Físicas 2024-2026
  B. IVA — Tasas, acreditamiento, DIOT
  C. IMSS / INFONAVIT / SAR — Cuotas 2024
  D. CFDI 4.0 — Tipos, cancelación, complementos
  E. Comercio Exterior — IGI, DTA, pedimentos, valor en aduana
  F. TIGIE — Fracciones arancelarias para Fourgea (filtros) y Triple R (aceites)
  G. MVE — Manifestación de Valor de Exportación/Importación
  H. VUCEM — Ventanilla Única, documentos aduaneros
  I. Contabilidad General — Catálogo SAT, DIOT, balanza
  J. Fechas y Declaraciones — Calendario fiscal SAT 2026
  K. NOM — Normas aplicables a filtros y aceites industriales
  L. T-MEC / USMCA — Reglas de origen

Uso: python3 seed_knowledge.py
"""

import os, sys
import psycopg2
from psycopg2.extras import execute_values

DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://mystic_user:MysticSecure2026!@localhost:5432/mystic_db"
)

# ──────────────────────────────────────────────────────────────────────────────
# BASE DE CONOCIMIENTO
# Formato: (topic, subtopic, title, content, source, keywords, year)
# ──────────────────────────────────────────────────────────────────────────────

KNOWLEDGE = [

# ═══════════════════════════════════════════════════════════════════
# A. ISR — IMPUESTO SOBRE LA RENTA
# ═══════════════════════════════════════════════════════════════════

("isr","personas_morales","Tasa ISR Personas Morales 2024-2026",
"""La tasa del Impuesto Sobre la Renta para personas morales en México es del 30% sobre la utilidad fiscal del ejercicio.
Base legal: Artículo 9 de la Ley del ISR (LISR).
La utilidad fiscal = ingresos acumulables - deducciones autorizadas - PTU pagada.
Ejemplo: Fourgea Mexico SA de CV con utilidad fiscal de $1,000,000 MXN paga $300,000 de ISR.""",
"LISR Art. 9","ISR personas morales tasa 30% utilidad fiscal SA de CV",2026),

("isr","personas_morales","Pagos Provisionales ISR Personas Morales — Art. 14 LISR",
"""Las personas morales deben realizar pagos provisionales mensuales de ISR a más tardar el día 17 del mes inmediato siguiente.
Cálculo: Coeficiente de utilidad (CU) x ingresos nominales del período = utilidad estimada x 30% = pago provisional.
Coeficiente de utilidad: utilidad fiscal del ejercicio anterior / ingresos nominales del mismo ejercicio.
Para el primer ejercicio se usa CU de 0.2 si no hay ejercicio previo.
El pago provisional es acumulativo: se calcula desde enero hasta el mes que corresponde y se restan pagos anteriores.""",
"LISR Art. 14","pagos provisionales ISR mensual coeficiente utilidad 30%",2026),

("isr","personas_morales","ISR Anual Personas Morales — Presentación",
"""Las personas morales deben presentar la declaración anual de ISR dentro de los 3 meses siguientes al cierre del ejercicio.
Para ejercicio enero-diciembre → presentar a más tardar el 31 de marzo del año siguiente.
Fourgea Mexico SA de CV: cierre 31 diciembre 2025 → declaración anual a más tardar 31 marzo 2026.
Si resulta saldo a favor, se puede compensar o solicitar devolución.""",
"LISR Art. 9, 76","declaración anual personas morales marzo cierre ejercicio",2026),

("isr","personas_morales","Deducciones Autorizadas ISR Personas Morales",
"""Son deducciones autorizadas para personas morales (Art. 25 LISR):
1. Devoluciones, descuentos y bonificaciones
2. Costo de lo vendido (COGS)
3. Gastos con comprobante fiscal (CFDI)
4. Inversiones (depreciación): maquinaria industrial 10%, equipo transporte 25%, computadoras 30%, edificios 5%
5. Créditos incobrables
6. Pérdidas por caso fortuito o fuerza mayor
7. Cuotas IMSS patronales
8. INFONAVIT patronal
9. Intereses devengados
10. PTU pagada en el ejercicio
Requisito: los gastos deben estar ESTRICTAMENTE INDISPENSABLES para la actividad y respaldados con CFDI 4.0.""",
"LISR Art. 25-28","deducciones autorizadas gastos CFDI depreciación costo vendido",2026),

("isr","personas_morales","PTU — Participación de los Trabajadores en las Utilidades",
"""La PTU es el 10% de la renta gravable (utilidad fiscal ajustada para PTU según Art. 9 LISR).
Se reparte dentro de los 60 días siguientes a la presentación de la declaración anual.
Para personas morales: plazo máximo 60 días después del 31 de marzo = 30 de mayo.
La PTU pagada en el ejercicio ES deducible de ISR del siguiente ejercicio.
Tope individual por trabajador: el mayor entre: promedio de PTU últimos 3 años O 3 meses de salario.""",
"LISR Art. 9, LFT Art. 120","PTU 10% utilidades repartibles trabajadores 60 días",2026),

("isr","personas_fisicas","ISR Personas Físicas con Actividad Empresarial — Régimen General",
"""Personas físicas con actividad empresarial (importadores, comerciantes) tributan sobre utilidad.
Tarifa progresiva 2024 hasta 35% para ingresos mayores a $3,000,000 anuales.
Tramos principales:
- Hasta $125,900: 1.92%
- $125,900 - $1,000,856: tasa marginal 6.4%-17.92%
- $1,000,856 - $1,166,200: 21.36%
- $1,166,200 - $3,498,600: 23.52%-30%
- Más de $3,498,600: 35%
Obligaciones: CFDI, declaraciones mensuales, declaración anual en abril.""",
"LISR Art. 100-110, Tarifa Art. 152","ISR personas físicas actividad empresarial tarifa progresiva 35%",2026),

("isr","resico","RESICO — Régimen Simplificado de Confianza Personas Físicas",
"""RESICO aplica a personas físicas con ingresos hasta $3,500,000 anuales.
Tasa reducida sobre ingresos cobrados (no utilidad):
- Hasta $300,000: 1.0%
- $300,001 - $600,000: 1.1%
- $600,001 - $1,000,000: 1.5%
- $1,000,001 - $2,500,000: 2.0%
- $2,500,001 - $3,500,000: 2.5%
Ventaja: no lleva contabilidad compleja, no deduce gastos.
Limitación: no puede importar en nombre propio de forma habitual sin salir del régimen.
Declaración: mensual definitiva a más tardar día 17.""",
"LISR Art. 113-A al 113-J","RESICO régimen simplificado confianza tasa 1% 2.5% personas físicas",2026),

("isr","resico","RESICO Personas Morales — Régimen Simplificado de Confianza",
"""RESICO PM aplica a personas morales (excepto integrantes del sistema financiero) con ingresos hasta $35,000,000 anuales.
Tasa: 30% sobre utilidad, PERO con facilidades de deducción inmediata de inversiones al 100%.
Pueden optar por deducción de gastos por flujo de efectivo (cuando se pagan, no cuando se devengan).
No aplica: empresas del sistema financiero, controladoras, maquiladoras, RE (art. 72 LISR).""",
"LISR Art. 206-221","RESICO personas morales 35 millones deducción inmediata 100%",2026),

("isr","comercio_exterior","ISR en Operaciones de Importación",
"""En importaciones, los costos son deducibles de ISR cuando:
1. Están respaldados con pedimento aduanal + factura del proveedor extranjero
2. La mercancía fue efectivamente importada (consta en sistema SAAI/VUCEM)
3. El pago se realizó mediante sistema financiero (transferencia, cheque)
4. Se tiene el CFDI de gastos relacionados (agente aduanal, flete nacional, etc.)
El costo de importación incluye: valor en aduana + IGI + DTA + fletes + seguros nacionales.""",
"LISR Art. 27, SAT criterios","deducción costo importación pedimento factura extranjera agente aduanal",2026),

# ═══════════════════════════════════════════════════════════════════
# B. IVA — IMPUESTO AL VALOR AGREGADO
# ═══════════════════════════════════════════════════════════════════

("iva","tasas","Tasa IVA General México 2026",
"""La tasa general del Impuesto al Valor Agregado (IVA) en México es del 16%.
Base legal: Artículo 1° de la Ley del IVA (LIVA).
Esta tasa aplica a: enajenación de bienes, prestación de servicios, uso o goce temporal de bienes, importación.
La tasa del 16% está vigente desde el 1 de enero de 2014 (antes era 15% hasta 2009, luego 16% en 2010-2013, luego otra vez la reforma).
En 2026 la tasa sigue siendo 16%.""",
"LIVA Art. 1°","IVA 16% tasa general enajenación servicios importación 2026",2026),

("iva","tasas","Tasa IVA 0% — Actividades Gravadas al 0%",
"""Actividades gravadas a tasa 0% de IVA (Art. 2-A LIVA):
1. Alimentos no procesados: frutas, verduras, carnes, leche, huevo, tortillas, masa
2. Medicamentos de patente
3. Agua purificada en garrafón
4. Fertilizantes, herbicidas, plaguicidas (para siembra)
5. Maquinaria agrícola
6. Libros, periódicos, revistas (edición propia)
7. Enajenación de oro (más de 80% de pureza)
Importante: los filtros industriales y aceites para maquinaria NO están en tasa 0%, se gravan al 16%.""",
"LIVA Art. 2-A","IVA 0% alimentos medicamentos agua garrafón libros exento",2026),

("iva","tasas","Frontera Norte — IVA 8%",
"""En la región fronteriza norte (franja de 20km), la tasa de IVA es del 8% para:
- Enajenación de bienes en establecimientos físicos ubicados en la franja fronteriza norte
- Servicios prestados en esa región
Municipios: Tijuana, Mexicali, San Luis Río Colorado, Nogales, Agua Prieta, Ciudad Juárez, Ojinaga, Piedras Negras, Nuevo Laredo, Reynosa, Matamoros y otros municipios limítrofes.
Hermosillo NO está en franja fronteriza → IVA 16%.
Sonora: solo los municipios que colindan con EEUU tienen IVA 8%.""",
"LIVA Art. 1-C, Decreto 31-dic-2018","IVA 8% frontera norte Sonora Hermosillo Nogales Tijuana Ciudad Juárez",2026),

("iva","importacion","IVA en Importación de Bienes",
"""El IVA en importaciones se calcula sobre la base: valor en aduana + IGI + DTA + IEPS (si aplica).
Fórmula: (Valor aduana + IGI + DTA + IEPS) × 16% = IVA importación
El IVA de importación se paga al momento del despacho aduanal junto con el pedimento.
Es ACREDITABLE contra el IVA trasladado a clientes en la declaración mensual.
Ejemplo Fourgea: importa filtros por $100,000 USD (valor aduana $1,800,000 MXN)
  IGI 5% = $90,000 | DTA = $669.46 | Base IVA = $1,890,669.46 | IVA = $302,507.11
Este IVA se acredita en la declaración de IVA del mes del despacho.""",
"LIVA Art. 24-28","IVA importación acreditable base valor aduana IGI DTA 16%",2026),

("iva","declaracion","Declaración Mensual de IVA",
"""El IVA se declara mensualmente (no hay pagos provisionales, cada mes es definitivo).
Plazo: a más tardar el día 17 del mes siguiente.
Cálculo:
  IVA trasladado cobrado (ventas) - IVA acreditable pagado (compras/importaciones) = IVA a pagar o saldo a favor
Si hay saldo a favor: puede compensarse contra otros impuestos federales (ISR, retenciones) o solicitarse en devolución (plazo SAT: 40 días automática, 10 días si hay garantía).
Certificación IVA e IEPS: empresas con volumen alto pueden certificarse para devolución acelerada (5 días).""",
"LIVA Art. 5-D, 6","declaración IVA mensual día 17 saldo favor devolución compensación",2026),

("iva","diot","DIOT — Declaración Informativa de Operaciones con Terceros",
"""La DIOT (A-29) informa las operaciones con proveedores nacionales y extranjeros mensualmente.
Obligados: personas morales y físicas con actividad empresarial.
Plazo: dentro de los primeros 17 días del mes siguiente al período declarado.
Incluye: RFC proveedor, tipo operación (proveedor, arrendador, prestador de servicios, global), monto pagado, IVA pagado, IVA retenido.
Para proveedores extranjeros: se reporta en el tipo "04 - proveedor extranjero" con nombre en lugar de RFC.
Fourgea debe reportar a todos sus proveedores de filtros, incluyendo los de EEUU/China.""",
"CFF Art. 32 fracc. VIII, Regla miscelánea","DIOT A-29 proveedores extranjeros RFC IVA mensual declaración informativa",2026),

# ═══════════════════════════════════════════════════════════════════
# C. IMSS / INFONAVIT / SAR
# ═══════════════════════════════════════════════════════════════════

("imss","cuotas","Cuotas IMSS Patronales y Obreras 2024",
"""Cuotas IMSS sobre el Salario Base de Cotización (SBC):
ENFERMEDAD Y MATERNIDAD:
  - Prestaciones en especie cuota fija: 20.40% patronal sobre 1 SMGDF por trabajador
  - Excedente del 3 SMGDF: 1.10% patronal + 0.40% obrero
  - Prestaciones en dinero: 0.70% patronal + 0.25% obrero
INVALIDEZ Y VIDA: 1.75% patronal + 0.625% obrero
RETIRO (SAR): 2% patronal
CESANTÍA Y VEJEZ: 3.150% patronal + 1.125% obrero
GUARDERÍAS: 1% patronal
RIESGOS DE TRABAJO: prima variable (mínimo 0.50% clase I, hasta 7.59% clase V)
Total aproximado patronal: 26-33% del SBC
Total aproximado obrero: 2.375% del SBC
SMGDF 2026: $278.80 pesos/día (general)""",
"LSS Art. 28-38, Tabla de cuotas IMSS 2024","IMSS cuotas patronales obreras SBC cotización enfermedad invalidez retiro 2024",2026),

("imss","sbc","Integración del Salario Base de Cotización (SBC)",
"""El SBC incluye (Art. 27 LSS):
INCLUYE: salario diario, vacaciones, prima vacacional, aguinaldo, comisiones, horas extra habituales, gratificaciones, bonos, despensas que excedan 40% del SMG.
NO INTEGRA (topes Art. 27):
- Herramientas de trabajo
- Ahorro cuando es igual patronal/obrero y no disponible para trabajador
- Aportaciones al fondo de pensiones (AFORE)
- Despensas hasta 40% del SMG ($111.52/día 2026)
- Tiempo extra hasta 3 veces por semana y 3 horas/día que no excedan 50% SMG
TOPE SBC: 25 SMGDF = $6,970 pesos/día en 2026""",
"LSS Art. 27","SBC salario base cotización integración aguinaldo vacaciones prima despensa",2026),

("imss","avisos","Avisos Afiliatorios IMSS",
"""Movimientos afiliatorios:
ALTA: dentro de los 5 días hábiles siguientes a la fecha de ingreso del trabajador (o antes).
BAJA: dentro de los 5 días hábiles siguientes a la fecha de baja.
MODIFICACIÓN DE SALARIO: dentro de los 5 días hábiles al cambio.
Consecuencia de no avisar a tiempo: el patrón paga IMSS desde la fecha en que debió avisarse.
Modalidad de presentación: IDSE (IMSS Desde Su Empresa) o SUA (Sistema Único de Autodeterminación).
Pago de cuotas: mensual, los días 15-17 del mes siguiente. También puede ser bimestral para algunos conceptos.""",
"LSS Art. 15, 34, 37","avisos IMSS alta baja modificación 5 días hábiles IDSE SUA",2026),

("infonavit","aportaciones","INFONAVIT — Aportación Patronal",
"""El patrón debe aportar el 5% del SBC al INFONAVIT de cada trabajador.
Pago: bimestral, junto con cuotas IMSS de retiro/cesantía/vejez.
Vencimiento bimestral: enero-febrero → 17 de marzo; marzo-abril → 17 de mayo; etc.
El trabajador puede usarlo para crédito hipotecario o retirarlo al cumplir 65 años sin haber obtenido crédito.
Límite de aportación: no hay tope, se paga sobre el SBC hasta el tope de 25 SMGDF.
En importaciones: las aportaciones INFONAVIT son deducibles de ISR.""",
"Ley INFONAVIT Art. 29, 35","INFONAVIT 5% aportación bimestral crédito hipotecario SBC patronal",2026),

("sar","aportaciones","SAR / AFORE — Retiro, Cesantía y Vejez",
"""Subcuenta de retiro (SAR): 2% patronal del SBC.
Subcuenta de cesantía y vejez (RCV): 3.150% patronal + 1.125% obrero.
Total aportación al sistema de pensiones: 5.150% patronal + 1.125% obrero + 5% INFONAVIT = ~11.275% patronal.
Reforma pensionaria 2021: aportación patronal aumenta gradualmente hasta llegar al 13.875% en 2030.
Calendario de incremento: 2023: 7.5%, 2024: 9.5%, 2025: 11%, 2026: 12.5%, 2027: 13.875%
El trabajador puede consultar su saldo en la AFORE de su elección.""",
"LSS Art. 168-170, Reforma 2021","SAR AFORE retiro cesantía vejez 2% aportación pensiones reforma 2021",2026),

# ═══════════════════════════════════════════════════════════════════
# D. CFDI 4.0
# ═══════════════════════════════════════════════════════════════════

("cfdi","version","CFDI 4.0 — Versión Actual Obligatoria",
"""CFDI 4.0 es la versión vigente y obligatoria desde el 1 de enero de 2022 (prórroga hasta 1 abril 2023).
Principales cambios vs 3.3:
1. Datos del receptor obligatorios: nombre completo tal como aparece en el SAT, domicilio fiscal, régimen fiscal del receptor
2. Se incorpora campo "Exportación" (01-No aplica, 02-Definitiva, 03-Temporal, 04-Retorno de mercancías)
3. Campo "Periodicidad", "Meses" y "Año" para CFDI globales
4. Nuevo campo "ObjetoImp" por partida (si el concepto es objeto de impuesto o no)
5. Información de objetos de impuestos más detallada
Herramientas: SAT Verificador, el PAC (Proveedor Autorizado de Certificación) sella y timbra el XML.""",
"RMF 2023 Regla 2.7.3.1","CFDI 4.0 versión obligatoria receptor nombre domicilio régimen exportación",2026),

("cfdi","tipos","Tipos de CFDI — Comprobantes Fiscales",
"""Tipos de CFDI por tipo de comprobante:
I — INGRESO: emitido al vender bienes o servicios, cobrar honorarios, arrendamientos.
E — EGRESO: notas de crédito, devoluciones, descuentos (reduce la factura original).
P — PAGO: complemento de recepción de pagos (CRP), cuando el pago es en parcialidades o diferido.
N — NÓMINA: para pago de salarios y asimilados (lleva complemento de nómina 1.2).
T — TRASLADO: para amparar el transporte de mercancías, acompañado de carta porte.
Fourgea como importador: recibe CFDI I de proveedor nacional, emite CFDI I a sus clientes, emite CFDI P cuando cobra después.""",
"CFF Art. 29, 29-A","CFDI tipo ingreso egreso pago nómina traslado complemento recepción pagos",2026),

("cfdi","cancelacion","Cancelación de CFDI 4.0",
"""Para cancelar un CFDI se requiere aceptación del receptor en muchos casos.
Motivos de cancelación (catálogo SAT):
01 - Comprobante emitido con errores con relación
02 - Comprobante emitido con errores sin relación
03 - No se llevó a cabo la operación
04 - Operación nominativa relacionada en una factura global
Plazos para cancelar:
- Mismo ejercicio fiscal: hasta el último día del año (31 de diciembre).
- Ejercicios anteriores: NO se puede cancelar (solo se emite EGRESO/nota de crédito).
El receptor tiene 72 horas para aceptar o rechazar la cancelación desde el portal SAT.""",
"RMF 2023 Regla 2.7.4","cancelación CFDI motivo 01 02 03 04 plazo 72 horas aceptación receptor",2026),

("cfdi","comercio_exterior","Complemento Comercio Exterior en CFDI",
"""El Complemento de Comercio Exterior (versión 1.1) se agrega al CFDI cuando se exporta.
Datos requeridos:
- TipoOperación: 1=Exportación, 2=Importación (solo para retorno de mercancías exportadas temporalmente)
- ClaveDePedimento: A1 (exportación definitiva), etc.
- CertificadoOrigen: si se emitirá certificado de origen T-MEC/otros
- Subdivisión: 0 o 1 si la mercancía se divide
- Datos del receptor en el extranjero: nombre, RFC (si aplica), domicilio
- Mercancías: fracción arancelaria, cantidad, unidad, valor unitario en dólares
Se usa para facturar a clientes en el extranjero y acompañar el pedimento de exportación.""",
"SAT Complemento Comercio Exterior 1.1","complemento comercio exterior CFDI exportación fracción arancelaria pedimento A1",2026),

("cfdi","carta_porte","Complemento Carta Porte 2.0",
"""El Complemento Carta Porte (versión 2.0) es obligatorio para el traslado de mercancías en territorio nacional.
Aplica cuando el propietario de la mercancía o el transportista emite CFDI tipo T (Traslado) o I (Ingreso con servicio de transporte).
Datos requeridos: puntos de origen y destino con coordenadas, autotransporte (placa, permiso SCT), operador (nombre, licencia), mercancías (peso, dimensiones, fracción arancelaria si aplica).
Para importaciones: cuando la mercancía ya está en México y se mueve del puerto/aduana al almacén del importador (Fourgea), el transportista debe emitir CFDI con Carta Porte.
Multa por no tenerlo: retención de la mercancía y multa de $4,000 a $16,000 pesos.""",
"CFF Art. 29, NOM-SCT Carta Porte 2.0","carta porte complemento traslado mercancías autotransporte permiso SCT placa operador",2026),

# ═══════════════════════════════════════════════════════════════════
# E. COMERCIO EXTERIOR — IGI, DTA, VALOR EN ADUANA
# ═══════════════════════════════════════════════════════════════════

("comercio_exterior","igi","IGI — Impuesto General de Importación",
"""El IGI (Impuesto General de Importación) se calcula aplicando la tasa de la fracción arancelaria (TIGIE) al valor en aduana.
Fórmula: Valor en aduana × tasa IGI% = IGI a pagar
Ejemplo: Filtros 8421.29.01 con tasa 5%, valor aduana $1,000,000 MXN → IGI = $50,000 MXN
Tasas comunes para productos Fourgea:
- Filtros industriales 8421.x: 5% o 7% (depende sub-partida)
- Partes de filtros 8421.99: 5%
- Juntas y empaques 8484.x: 5% o libre
Tasas para productos T-MEC (EEUU/Canadá): generalmente 0% (ver reglas de origen)
El IGI se paga junto con el pedimento al momento del despacho aduanal.""",
"LA Art. 53, TIGIE","IGI impuesto importación tasa TIGIE fracción arancelaria valor aduana despacho",2026),

("comercio_exterior","dta","DTA — Derecho de Trámite Aduanero 2026",
"""El DTA (Derecho de Trámite Aduanero) es una cuota fija que se paga por cada pedimento de importación.
Monto 2026: $669.46 pesos por pedimento (actualizado anualmente por inflación en el DOF).
Aplica a importaciones definitivas (régimen C1, A4, etc.) y temporales.
Excepciones que pagan DTA diferente:
- Importaciones exentas o con franquicia: $289.00
- Régimen IMMEX temporal: $289.00 por pedimento
- Correos y mensajería (courier): $191.00
El DTA es deducible de ISR como gasto de importación y forma parte de la base para calcular el IVA de importación.""",
"LFD Art. 49","DTA derecho trámite aduanero $669.46 2026 pedimento importación definitiva",2026),

("comercio_exterior","valor_aduana","Valor en Aduana — Métodos de Valoración",
"""El valor en aduana es la base para calcular IGI e IVA de importación.
Método 1 (principal): Valor de transacción = precio pagado o por pagar + adiciones:
  Adiciones obligatorias: comisiones de compra, embalaje, flete hasta puerto de entrada, seguro, regalías, parte del producto de reventa que vaya al vendedor.
Conversión a pesos: al tipo de cambio oficial publicado por Banxico el día anterior al despacho.
Por incoterm:
- FOB: precio FOB + flete internacional + seguro (para llegar a CIF)
- CIF: ya incluye costo, flete y seguro → usar directamente como valor aduana
- EXW: EXW + carga + flete hasta frontera + seguro
- DDP: restar todos los impuestos y costos en destino al precio DDP
El valor en aduana NUNCA puede ser inferior al precio de lista o factura comercial sin justificación documentada.""",
"LA Art. 64-78","valor aduana métodos valoración OMC GATT transacción FOB CIF EXW DDP",2026),

("comercio_exterior","pedimento","Tipos de Pedimento Aduanal",
"""Principales claves de pedimento:
C1 — Importación definitiva: mercancía queda en México de manera definitiva.
T1 — Importación temporal (IMMEX/maquiladora): regresa o se incorpora a producción.
G1 — Exportación definitiva: mercancía sale definitivamente de México.
A4 — Importación definitiva con pedimento consolidado.
V5 — Exportación temporal (para reparación, exposición, etc.)
F4 — Importación de retorno (lo que regresó de exportación temporal).
Para Fourgea: usa C1 principalmente para importar filtros y refacciones de EEUU/China.
Cada pedimento lleva: fecha y hora de pago, régimen, aduana de entrada, RFC del importador, valor en aduana, impuestos, guía/BL, fracción arancelaria de cada ítem.""",
"LA Art. 36, 37, 43","pedimento C1 T1 G1 importación definitiva temporal exportación régimen aduana",2026),

("comercio_exterior","agente_aduanal","Agente Aduanal — Obligaciones y Responsabilidades",
"""El Agente Aduanal actúa como representante legal del importador ante la aduana.
Responsabilidades del agente aduanal:
- Verificar fracción arancelaria correcta
- Determinar el valor en aduana correcto
- Verificar que la mercancía coincida con los documentos
- Presentar el pedimento y pagar impuestos
- Conservar la información por 5 años
El importador (Fourgea) también es responsable solidario de los impuestos.
Documentos que debe proporcionar Fourgea al agente:
  1. Factura comercial del proveedor (en inglés o con traducción)
  2. BL (Bill of Lading) o guía aérea (AWB)
  3. Lista de empaque (packing list)
  4. Certificado de origen (si aplica T-MEC)
  5. Permisos previos (si la mercancía lo requiere)
  6. MVE (Manifestación de Valor) firmada""",
"LA Art. 54-58, 163","agente aduanal responsabilidades fracción arancelaria factura BL packing list certificado origen",2026),

("comercio_exterior","ieps","IEPS en Importaciones",
"""El IEPS (Impuesto Especial sobre Producción y Servicios) aplica en la importación de:
- Combustibles: gasolina, diesel, turbosina (tasas variables 2026: gasolina magna ~$6.23/L)
- Bebidas alcohólicas: 26.5% a 53%
- Tabacos: 160% + cuota fija
- Alimentos de alta densidad calórica (>275 kcal/100g): 8%
- Bebidas con azúcar: $1.46/L
Para Triple R Oil: importar aceites lubricantes (27101991, 27101999) puede causar IEPS de combustibles si no se documenta correctamente como lubricante (no combustible). Los aceites lubricantes en general NO pagan IEPS.
Para Fourgea: filtros industriales NO pagan IEPS.""",
"LIEPS Art. 1, 2","IEPS combustibles gasolina aceites lubricantes bebidas tabacos importación cuota fija",2026),

# ═══════════════════════════════════════════════════════════════════
# F. TIGIE — FRACCIONES ARANCELARIAS FOURGEA (Filtros)
# ═══════════════════════════════════════════════════════════════════

("tigie","filtros","TIGIE — Capítulo 84: Filtros y Aparatos para Filtrar Líquidos (Fourgea)",
"""Fracciones arancelarias para filtros industriales (Fourgea Mexico):
8421.21.01 — Aparatos para filtrar o depurar agua, diseñados para uso doméstico: IGI 15%
8421.21.99 — Los demás aparatos para filtrar/depurar agua: IGI 7%
8421.23.01 — Filtros de aceite para motores de vehículos: IGI 5%
8421.29.01 — Filtros de aceite para maquinaria industrial (centrifugadores): IGI 5%
8421.29.99 — Los demás aparatos para filtrar o depurar líquidos: IGI 5% (fracción principal Fourgea)
8421.31.01 — Filtros de entrada de aire para motores de vehículos: IGI 5%
8421.39.01 — Filtros de aire para maquinaria industrial: IGI 5%
8421.39.99 — Los demás filtros para gases: IGI 5% (filtros industriales genéricos)
Con T-MEC (origen EEUU o Canadá): 0% IGI para todas las sub-partidas de 8421""",
"TIGIE SE Capítulo 84","TIGIE 8421 filtros industriales agua aceite aire IGI 5% 7% T-MEC Fourgea",2026),

("tigie","filtros_partes","TIGIE — Partes y Refacciones de Filtros (Fourgea)",
"""Partes y componentes para filtros industriales:
8421.99.01 — Partes de centrífugas y filtros: IGI 5%
8421.99.99 — Las demás partes de filtros: IGI 5%
8484.10.01 — Juntas metálicas: IGI 5%
8484.20.01 — Juegos o surtidos de juntas de distinta composición: IGI 5%
7304.41.01 — Tubos sin costura de acero para filtros/industria química: IGI 5%
3926.90.99 — Artículos de plástico para usos industriales (housing de filtros): IGI 5%
3917.32.99 — Tubos y mangueras de plástico: IGI 10% (exento T-MEC)
4016.93.99 — Juntas y empaques de hule: IGI 5%
Para T-MEC: verificar regla de origen específica de cada fracción (cambio de clasificación arancelaria o contenido regional).""",
"TIGIE SE Cap. 84, 39, 73, 84","TIGIE partes filtros 8421.99 8484 juntas empaques tubos acero plástico hule",2026),

("tigie","bombas","TIGIE — Bombas y Sistemas de Filtración (Fourgea)",
"""Fracciones para bombas usadas en sistemas de filtración:
8413.11.01 — Bombas para combustibles (gasolineras): IGI 10%
8413.50.01 — Bombas centrífugas de una etapa: IGI 5%
8413.60.99 — Las demás bombas de desplazamiento rotatorio: IGI 5%
8413.70.99 — Las demás bombas para líquidos: IGI 5%
8413.91.99 — Partes de bombas: IGI 5%
9026.10.99 — Instrumentos para medir caudal de líquidos: IGI 5%
9026.20.99 — Instrumentos para medir presión: IGI 5%
T-MEC (EEUU/Canadá): IGI 0% en todas estas fracciones si se cumple regla de origen.""",
"TIGIE SE Cap. 84, 90","TIGIE bombas centrífugas 8413 instrumentos medición caudal presión 9026 filtración",2026),

# ═══════════════════════════════════════════════════════════════════
# G. TIGIE — TRIPLE R OIL (Aceites)
# ═══════════════════════════════════════════════════════════════════

("tigie","aceites","TIGIE — Capítulo 27: Aceites y Lubricantes (Triple R Oil)",
"""Fracciones arancelarias para aceites (Triple R Oil México):
2710.12.01 — Gasolinas para motor: IGI libre (cubierto por IEPS), regulado por CRE
2710.19.01 — Aceites lubricantes para motores: IGI libre (0%), IVA 16%
2710.19.11 — Aceites minerales, base lubricante: IGI libre
2710.19.99 — Los demás aceites de petróleo: IGI libre
2710.20.01 — Aceites de petróleo con contenido de biodiesel: IGI libre
2710.91.01 — Residuos de aceites: IGI libre
2712.90.99 — Parafinas y ceras: IGI 5%
Importante: la importación de aceites lubricantes NO causa IEPS (no son combustible automotriz).
Sin embargo requieren: certificado de análisis de composición y en algunos casos permiso previo de la CRE.""",
"TIGIE SE Cap. 27","TIGIE 2710 aceites lubricantes petróleo motor IGI libre CRE IEPS Triple R",2026),

("tigie","aceites_partes","TIGIE — Envases y Equipo para Aceites (Triple R)",
"""Fracciones para envases y equipo relacionado con aceites:
3923.30.99 — Damajuanas, botellas, frascos de plástico (envases aceite): IGI 5%
7310.10.01 — Depósitos de hierro o acero (tambos 200L): IGI 5%
8421.23.99 — Filtradores de aceite industrial (en línea): IGI 5%
8479.89.99 — Máquinas para filtrar/recuperar aceite: IGI 5%
Permisos previos para aceites:
- Registro como Organización del Sector Privado (OSP) ante CRE si se comercializa al menudeo
- Aviso de inicio de operaciones si se importa para reventa
Sin permiso previo de COFEPRIS para aceites industriales no alimenticios.""",
"TIGIE SE Cap. 27, 39, 73, 84","aceites envases tambos plástico 200L depósitos hierro acero CRE permiso",2026),

# ═══════════════════════════════════════════════════════════════════
# H. MVE — MANIFESTACIÓN DE VALOR
# ═══════════════════════════════════════════════════════════════════

("mve","concepto","MVE — Manifestación de Valor en Importación",
"""La MVE (Manifestación de Valor) es un documento obligatorio que el importador firma para declarar el valor en aduana.
Obligación: siempre que se importe de manera definitiva, independientemente del valor (Art. 59-A LA).
Elementos que debe contener:
1. Nombre/razón social y RFC del importador (Fourgea: E080820LC2)
2. Fecha de elaboración
3. Descripción, cantidad y precio unitario de la mercancía
4. Incoterm acordado con el proveedor
5. Valor de transacción (precio pagado/por pagar)
6. Adiciones al valor: flete internacional, seguro, comisiones, embalaje, otras
7. Declaración bajo protesta de decir verdad que la información es correcta
La MVE se entrega al agente aduanal y él la adjunta al pedimento.""",
"LA Art. 59-A, ACA Art. 161-168","MVE manifestación valor obligatoria importación definitiva RFC incoterm adiciones",2026),

("mve","calculo_fob","MVE — Cálculo del Valor en Aduana por Incoterm FOB",
"""Para incoterm FOB (Free on Board):
El precio FOB NO incluye flete internacional ni seguro.
Valor en aduana = Valor FOB + Flete internacional + Seguro internacional
Ejemplo:
  Precio FOB filtros EEUU: $10,000 USD
  Flete marítimo EEUU-Manzanillo: $800 USD
  Seguro (0.5% del valor): $50 USD
  Valor en aduana: $10,850 USD × tipo de cambio del día
  Si TC = $17.50: valor aduana = $189,875 MXN
  IGI 5%: $9,493.75 MXN
  DTA: $669.46 MXN
  Base IVA: $200,038.21 MXN
  IVA 16%: $32,006.11 MXN
  Total impuestos a pagar: $42,169.32 MXN""",
"LA Art. 64, RMCE","MVE FOB cálculo valor aduana flete seguro IGI IVA DTA ejemplo",2026),

("mve","calculo_cif","MVE — Cálculo del Valor en Aduana por Incoterm CIF",
"""Para incoterm CIF (Cost, Insurance and Freight):
El precio CIF ya incluye costo, seguro y flete hasta puerto de destino.
Valor en aduana = Valor CIF (sin adiciones adicionales de flete/seguro)
Ejemplo:
  Precio CIF filtros China: $15,000 USD
  Valor en aduana: $15,000 USD × TC $17.50 = $262,500 MXN
  IGI 5%: $13,125 MXN
  DTA: $669.46 MXN
  Base IVA: $276,294.46 MXN
  IVA 16%: $44,207.11 MXN
  Total impuestos: $58,001.57 MXN
Nota: Si el incoterm es DAP o DDP el vendedor paga más costos, pero el valor en aduana México se calcula CON el flete/seguro hasta frontera mexicana, sin los costos posteriores.""",
"LA Art. 64, RMCE","MVE CIF valor aduana incluye flete seguro costo China EEUU importación",2026),

("mve","minimo","Valor Mínimo de la DTA y Límites MVE",
"""DTA mínima 2026: $669.46 pesos por pedimento (sin importar el valor de la mercancía).
Franquicia personal: hasta $500 USD por persona en viajero — sin pedimento formal.
Importaciones menores (paquetería courier):
  - Hasta $50 USD: libre de impuestos y sin pedimento
  - $50 a $1,000 USD: pedimento simplificado, IGI fijo 17%
  - Más de $1,000 USD: pedimento normal completo
Para importaciones de empresa (Fourgea): siempre pedimento completo con MVE, sin importar el monto.""",
"LFD Art. 49, LA Art. 88","DTA mínima $669.46 franquicia viajero courier $50 $1000 pedimento simplificado",2026),

# ═══════════════════════════════════════════════════════════════════
# I. VUCEM / NOM / PERMISOS PREVIOS
# ═══════════════════════════════════════════════════════════════════

("vucem","concepto","VUCEM — Ventanilla Única de Comercio Exterior México",
"""VUCEM es el portal electrónico del gobierno mexicano para tramitar documentos de comercio exterior.
Portal: www.ventanillaunica.gob.mx
Principales trámites en VUCEM:
- Permisos de importación/exportación (SE, COFEPRIS, SEMARNAT, SAGARPA)
- Certificados fitosanitarios y zoosanitarios
- Autorizaciones ITAR/EAR para mercancías de doble uso
- Declaración de valor en aduana (MVE electrónica)
- E.document (documentos electrónicos)
Para filtros industriales (Fourgea): generalmente NO se requieren permisos previos en VUCEM, salvo si contienen materiales peligrosos o clorofluorocarbonos (CFCs) como refrigerantes.
Para aceites (Triple R): no requieren permiso VUCEM, solo CRE si se comercializan.""",
"VUCEM, RMCE","VUCEM portal ventanilla única permisos importación exportación SE COFEPRIS trámites",2026),

("vucem","nom_filtros","NOM Aplicables a Filtros Industriales (Fourgea)",
"""Normas Oficiales Mexicanas aplicables a filtros y equipo industrial:
NOM-001-SEDE-2012: Instalaciones eléctricas — aplica si el filtro tiene componente eléctrico/electrónico.
NOM-005-STPS-1998: Condiciones de seguridad en manejo de sustancias químicas — aplica en planta.
NOM-010-STPS-2014: Agentes químicos contaminantes — para filtros que manejan sustancias.
NOM-004-SE-2021: Información comercial de seguridad en productos peligrosos — etiquetado.
NOM-050-SCFI-2004: Información comercial general — aplica a todos los productos importados para venta en México.
Filtros sin componente eléctrico y sin sustancias reguladas: generalmente sin NOM de importación.
Verificación: consultar el "Catálogo de Regulaciones, Restricciones y Prohibiciones de Importación" de la SE.""",
"SE Catálogo RRPI, NOM","NOM filtros industriales eléctrico STPS SCFI SEDE importación regulaciones restricciones",2026),

("vucem","poa","POA — Poder Otorgado al Agente Aduanal",
"""El POA (Poder Otorgado al Agente Aduanal) es el documento que autoriza al agente a actuar en nombre del importador.
Tipos:
1. General: cubre todas las operaciones
2. Específico: cubre solo un pedimento determinado
Formalidades: No requiere notarización, es suficiente el formato oficial con firma del representante legal de la empresa.
Registro en SAAI: el importador debe registrar su RFC y POA en el sistema SAAI (Sistema Aduanero Automatizado Integral).
RFC Fourgea: E080820LC2
Responsabilidad: con POA, el importador es solidariamente responsable de los actos del agente aduanal.""",
"LA Art. 54, 59","POA poder agente aduanal RFC importador SAAI general específico pedimento",2026),

# ═══════════════════════════════════════════════════════════════════
# J. CONTABILIDAD GENERAL / CATÁLOGO SAT
# ═══════════════════════════════════════════════════════════════════

("contabilidad","catalogo_sat","Catálogo de Cuentas SAT — Grupos Principales",
"""El SAT define el catálogo mínimo de cuentas para Contabilidad Electrónica (Art. 28 CFF):
ACTIVO (1):
  100 — Caja y Efectivo
  102 — Bancos
  105 — Clientes/Cuentas por cobrar
  106 — Documentos por cobrar
  108 — IVA acreditable (pagado)
  115 — Inventarios
  120 — Activo Fijo (maquinaria, equipo, edificios)
  121 — Depreciación acumulada
PASIVO (2):
  201 — Proveedores nacionales
  205 — Proveedores extranjeros (importaciones)
  206 — Documentos por pagar
  208 — IVA trasladado (cobrado a clientes)
  209 — IVA por pagar (neto)
  213 — ISR por pagar
  214 — Retenciones IMSS por enterar
CAPITAL (3):
  301 — Capital social
  305 — Utilidades retenidas
  306 — Utilidad/Pérdida del ejercicio
INGRESOS (4):
  401 — Ventas nacionales
  402 — Ventas exportación
  403 — Devoluciones sobre ventas
COSTOS (5):
  501 — Costo de ventas
  502 — Costo de importación (IGI + DTA + fletes)
GASTOS (6):
  601 — Gastos de administración
  602 — Gastos de venta
  603 — Honorarios agente aduanal
  604 — Fletes y acarreos
  605 — Seguros""",
"CFF Art. 28, Anexo 24 RMF","catálogo cuentas SAT contabilidad electrónica activo pasivo capital ingresos costos gastos",2026),

("contabilidad","asiento_importacion","Asiento Contable para Importación de Mercancía",
"""Registro contable de una importación típica (Fourgea):
EJEMPLO: Filtros importados valor en aduana $200,000 MXN, IGI 5% = $10,000, DTA $669, IVA $33,707:
DEBE:
  115 Inventarios ................ $210,669 (valor + IGI + DTA)
  108 IVA acreditable pagado ..... $33,707
HABER:
  205 Proveedores extranjeros ..... $200,000 (valor de la mercancía)
  102 Bancos (pago impuestos aduana) $44,376 (IGI + DTA + IVA)
Al pagar al proveedor extranjero (30 días después):
DEBE:
  205 Proveedores extranjeros ..... $200,000
HABER:
  102 Bancos ...................... $200,000
IVA en declaración mensual:
  IVA acreditable $33,707 — IVA trasladado cobrado = saldo a pagar o favor""",
"CINIF NIF A-1, B-3","asiento contable importación inventarios IVA acreditable proveedores extranjeros banco",2026),

("contabilidad","asiento_nomina","Asiento Contable Nómina",
"""Registro contable de nómina mensual (ejemplo empleado $20,000 sueldo bruto):
Cuotas aproximadas: IMSS patronal 26% = $5,200 | INFONAVIT 5% = $1,000 | ISR retenido empleado $2,000 | IMSS obrero 2.375% = $475
DEBE:
  601 Gastos de administración (sueldos) ..... $20,000
  601 Gastos de administración (IMSS pat) .... $5,200
  601 Gastos de administración (INFONAVIT) ... $1,000
HABER:
  102 Bancos (neto pagado al empleado) ....... $17,525 ($20,000 - $2,000 ISR - $475 IMSS obrero)
  213 ISR retenido por enterar ............... $2,000
  214 IMSS/INFONAVIT por enterar ............. $6,675 ($5,200 pat + $1,000 info + $475 obrero)
Al pagar al SAT (ISR retenido día 17):
  213 ISR retenido → Bancos
Al pagar al IMSS/INFONAVIT (día 17):
  214 IMSS/INFONAVIT por enterar → Bancos""",
"CINIF NIF D-3","asiento nomina sueldo IMSS patronal INFONAVIT ISR retenido banco",2026),

("contabilidad","conciliacion","Conciliación Contable-Fiscal ISR",
"""La conciliación entre resultado contable y fiscal se hace en la declaración anual:
Resultado contable (según estados financieros)
+ Ingresos fiscales no contables (anticipos cobrados, etc.)
- Ingresos contables no fiscales (dividendos entre empresas del mismo grupo)
+ Gastos contables no deducibles: multas, recargos, donativos exceso, gastos sin CFDI, viáticos sin tarjeta, gasolina efectivo > $2,000
- Deducciones fiscales no contables: deducción inmediata inversiones (si se optó)
= Utilidad fiscal antes de PTU
- PTU pagada en el ejercicio
= Utilidad fiscal
× 30% = ISR del ejercicio
- Pagos provisionales realizados
= ISR a cargo o saldo a favor""",
"LISR Art. 9, 25-28","conciliación contable fiscal utilidad deducible gastos no deducibles PTU ISR anual",2026),

# ═══════════════════════════════════════════════════════════════════
# K. CALENDARIO FISCAL SAT 2026
# ═══════════════════════════════════════════════════════════════════

("calendario","declaraciones","Calendario de Declaraciones Fiscales 2026",
"""Obligaciones fiscales mensuales (personas morales):
Día 17 de cada mes: IVA definitivo del mes anterior
Día 17 de cada mes: ISR pago provisional del mes anterior
Día 17 de cada mes: Retenciones ISR de trabajadores (nómina)
Día 17 de cada mes: Retenciones ISR de honorarios, arrendamiento, etc.
Día 17 de cada mes: DIOT (proveedores)
Día 17 de cada mes: IMSS cuotas obreras y patronales (mensual)
Bimestral (días 17): IMSS e INFONAVIT para aportaciones de retiro/vivienda
Obligaciones anuales:
31 de marzo: Declaración anual ISR personas morales ejercicio anterior
30 de abril: Declaración anual ISR personas físicas
Informativas (anuales):
Febrero: Declaración de préstamos, aportaciones de capital y dividendos pagados a extranjeros
Marzo: Contabilidad electrónica (balanza anual) en Portal SAT""",
"SAT Calendario Fiscal 2026","calendario fiscal SAT 2026 día 17 declaraciones IVA ISR IMSS DIOT nómina",2026),

("calendario","cfdi_nomina","CFDI de Nómina — Plazos de Timbrado",
"""El CFDI de nómina debe timbrarse:
- El mismo día en que se realiza el pago al trabajador, O
- A más tardar el día 17 del mes siguiente al que corresponde el pago (opción fiscal vigente hasta 2026)
Complemento de Nómina versión 1.2 es el vigente.
Si el ejercicio no está cerrado, se puede corregir con CFDI complementario.
Conceptos que van en el CFDI nómina:
  Percepciones: sueldos, horas extra, comisiones, despensas, prima vacacional, aguinaldo
  Deducciones: ISR retenido, IMSS obrero, INFONAVIT descuento crédito
  Otros pagos: subsidio para el empleo (si aplica)
El empleado puede verificar su CFDI de nómina en el portal del SAT para su declaración anual.""",
"RMF 2023, Regla 3.12.4","CFDI nómina timbrado día 17 complemento 1.2 percepciones deducciones subsidio empleo",2026),

# ═══════════════════════════════════════════════════════════════════
# L. T-MEC / USMCA — REGLAS DE ORIGEN
# ═══════════════════════════════════════════════════════════════════

("tmec","reglas_origen","T-MEC — Reglas de Origen para Importar con Tasa 0%",
"""Para aprovechar la tasa 0% de IGI del T-MEC (EEUU-México-Canadá), la mercancía debe cumplir la regla de origen:
1. ORIGINARIA: fabricada 100% en el territorio T-MEC con insumos de la región, O
2. CAMBIO DE CLASIFICACIÓN ARANCELARIA: los insumos no originarios cambian de fracción al 4 dígitos (o más), O
3. CONTENIDO REGIONAL: al menos 60% del valor de la mercancía es de origen T-MEC (método transacción) o 50% (método costo neto)
Para filtros industriales (8421.x):
  Regla: cambio de posición (CC) desde cualquier otro capítulo + si no cumple, RVC 60%
Para aceites lubricantes (2710.x):
  Regla: cambio de subpartida (CS) o elaboración en territorio T-MEC
Documentación requerida: Certificado de Origen T-MEC (puede ser en la factura o documento separado firmado por exportador/productor/importador).""",
"T-MEC Cap. 4, Anexo 4-B","T-MEC USMCA reglas origen tasa 0% IGI cambio clasificación contenido regional 60% certificado",2026),

("tmec","certificado_origen","Certificado de Origen T-MEC — Formato y Vigencia",
"""El Certificado de Origen T-MEC NO tiene un formato oficial obligatorio (a diferencia del TLCAN que usaba el Formulario A).
En T-MEC la certificación puede hacerse en:
- La propia factura comercial
- Una declaración independiente firmada
Debe contener mínimo:
1. Identificación del certificador (exportador, productor o importador)
2. Nombre y dirección del exportador, productor e importador
3. Descripción del bien y fracción arancelaria a 6 dígitos HS
4. Criterio de origen (A=totalmente obtenido, B=producido enteramente, C=cambio de clasificación, D=RVC)
5. Período de validez (máximo 12 meses = para múltiples importaciones del mismo bien)
6. Declaración de veracidad y firma
El importador (Fourgea) puede conservar el certificado en lugar de enviarlo a la aduana, pero debe tenerlo disponible ante requerimiento.""",
"T-MEC Art. 5.2, 5.4","certificado origen T-MEC USMCA formato factura criterio A B C D vigencia 12 meses",2026),

# ═══════════════════════════════════════════════════════════════════
# M. CONTABILIDAD ELECTRÓNICA SAT
# ═══════════════════════════════════════════════════════════════════

("contabilidad_electronica","obligacion","Contabilidad Electrónica — Obligaciones Art. 28 CFF",
"""Obligados a llevar contabilidad electrónica (Art. 28 CFF):
- Personas morales (sin excepción)
- Personas físicas con actividad empresarial con ingresos > $2,000,000 anuales
Archivos que se envían al SAT (Portal):
1. CATÁLOGO DE CUENTAS: XML con la estructura de cuentas (Anexo 24 RMF). Se envía la primera vez que se usa y cuando hay modificaciones.
2. BALANZA DE COMPROBACIÓN: XML mensual con saldos iniciales, movimientos y saldos finales por cuenta. Se envía a más tardar el día 25 del mes siguiente (o 27 para personas físicas).
3. AUXILIAR DE CUENTAS: solo cuando el SAT lo solicite específicamente (no es envío regular).
4. PÓLIZAS: solo cuando el SAT lo solicite en auditoría.
Para Fourgea Mexico SA de CV: obligada a enviar balanza mensual.""",
"CFF Art. 28, RMF 2023 Regla 2.8.1","contabilidad electrónica Art 28 CFF balanza XML catálogo cuentas Anexo 24 día 25",2026),

("contabilidad_electronica","estad_financieros","Estados Financieros Básicos",
"""Estados financieros que toda empresa debe preparar:
1. BALANCE GENERAL (Estado de Situación Financiera):
   Activo total = Pasivo total + Capital contable
   Fourgea: Activo circulante (caja, cuentas por cobrar, inventario) + Activo fijo (maquinaria, equipo) vs. Pasivo (proveedores, créditos) + Capital
2. ESTADO DE RESULTADOS:
   Ventas - Devoluciones = Ventas netas
   Ventas netas - Costo de ventas = Utilidad bruta
   Utilidad bruta - Gastos operativos = Utilidad de operación
   Utilidad de operación - ISR - PTU = Utilidad neta
3. ESTADO DE FLUJO DE EFECTIVO: entradas y salidas reales de efectivo
4. ESTADO DE VARIACIONES EN CAPITAL: cambios en patrimonio
Para importadoras: el costo de ventas incluye costo de importación (valor aduana + IGI + DTA + fletes).""",
"CINIF NIF A-3, B-1, B-2, B-4","balance general estado resultados flujo efectivo capital activo pasivo utilidad neta",2026),

# ═══════════════════════════════════════════════════════════════════
# N. RETENCIONES
# ═══════════════════════════════════════════════════════════════════

("retenciones","honorarios","Retención ISR por Honorarios",
"""Cuando una persona moral paga honorarios a una persona física, debe retener:
ISR: 10% del monto del honorario pagado
IVA: si el prestador está en régimen con IVA, el receptor puede retener 2/3 del IVA (10.67% del total) o el 100% si es persona moral.
Obligaciones:
1. Retener el ISR y enterar el día 17 del mes siguiente
2. Emitir CFDI de retenciones e información de pagos
3. Incluir la retención en la DIOT
Ejemplo: Fourgea paga $10,000 a un consultor persona física:
  - ISR retenido: $1,000 (10%)
  - IVA del consultor: $1,600 (16%)
  - IVA retenido: $1,066.67 (2/3 del IVA)
  - Pago neto al consultor: $9,533.33""",
"LISR Art. 106, LIVA Art. 1-A","retención honorarios persona moral física 10% ISR IVA 2/3 consultor",2026),

("retenciones","pagos_extranjero","Retención ISR Pagos a Extranjeros",
"""Cuando Fourgea paga al proveedor extranjero (EEUU, China, Europa):
Si el pago es por BIENES: no hay retención de ISR (la importación ya paga IGI).
Si el pago es por SERVICIOS (regalías, asistencia técnica, intereses):
  - Regalías por uso de patente: retención 25% o tasa del tratado (EEUU: 10%)
  - Asistencia técnica: retención 25% o tasa del tratado
  - Intereses a extranjeros: 4.9% a 35% según tipo y país
  - Dividendos: 10% retención (solo si se distribuyen)
México tiene tratados para evitar doble imposición con: EEUU, Canadá, España, Alemania, Francia, Japón, China y más de 70 países.
Aplica formulario W-8BEN del IRS para pagos a EEUU.""",
"LISR Art. 153-175, Tratados","retención ISR pago extranjero servicios regalías asistencia técnica tratado EEUU 10%",2026),

# ═══════════════════════════════════════════════════════════════════
# O. REGÍMENES ESPECIALES ADUANALES
# ═══════════════════════════════════════════════════════════════════

("aduanas","immex","IMMEX — Industria Manufacturera Maquiladora",
"""IMMEX permite importar temporalmente insumos para fabricar, transformar o reparar productos destinados a exportación, sin pagar IGI ni IVA de importación.
Tipos de programas IMMEX:
1. Controladora de empresas: varias empresas bajo una misma controladora
2. Industrial: fabricación o transformación de bienes para exportar
3. Servicios: actividades de servicios que se exportan
4. Albergue: empresa extranjera opera con instalaciones de empresa mexicana certificada
5. Proyecto específico: para un proyecto determinado de temporada
Para Fourgea/Triple R: no aplica IMMEX directamente (importan para vender en México, no para reexportar). Sin embargo, si en el futuro exportan productos que incorporan los filtros importados, podrían certificarse.""",
"Decreto IMMEX DOF 16-may-2006","IMMEX maquiladora importación temporal insumos fabricación exportación sin IGI IVA",2026),

("aduanas","recinto_fiscalizado","Recinto Fiscalizado Estratégico (RFE)",
"""El RFE permite almacenar, manejar, transformar y reparar mercancías extranjeras hasta por dos años sin pagar impuestos.
Operadores: empresas privadas que cuentan con autorización del SAT.
Diferencia con bodega aduanal: en RFE se pueden hacer más operaciones (transformación simple).
Para Fourgea: podría usar un RFE para almacenar inventario de filtros en frontera y despacharlos según pedidos, evitando pagar impuestos hasta que entren formalmente al mercado.
Para exportaciones (Triple R): un RFE permite consolidar aceites antes de exportar.
Plazo: 2 años prorrogables con autorización del SAT.""",
"LA Art. 135-A","recinto fiscalizado estratégico RFE almacenaje transformación sin impuestos 2 años",2026),

# ═══════════════════════════════════════════════════════════════════
# P. PRECIOS DE TRANSFERENCIA
# ═══════════════════════════════════════════════════════════════════

("precios_transferencia","concepto","Precios de Transferencia — Operaciones entre Partes Relacionadas",
"""Las operaciones entre partes relacionadas (empresas del mismo grupo) deben pactarse a precios de mercado (arm's length).
Fourgea y Triple R (mismo dueño Marco): son partes relacionadas.
Obligaciones para operaciones entre ellas:
1. Precio = como si fueran terceros independientes
2. Documentar mediante estudio de precios de transferencia si supera $13,000,000 de ingresos totales (o $3,000,000 en operaciones con partes relacionadas)
3. Declarar en la Declaración Informativa Múltiple (DIM) Anexo 9
Métodos aceptados: precio comparable no controlado (PCN), precio de reventa, costo adicionado, utilidad comparable, partición de utilidades.
Si la SAT rechaza los precios → ajuste fiscal + multas + recargos.""",
"LISR Art. 76 fracc. IX, 179-184","precios transferencia partes relacionadas arm's length documentación DIM Fourgea Triple R",2026),


# ═══════════════════════════════════════════════════════════════════
# Q. DEPRECIACIONES Y AMORTIZACIONES
# ═══════════════════════════════════════════════════════════════════

("isr","depreciacion","Tasas de Depreciación Fiscal LISR 2026",
"""Tasas anuales de depreciación fiscal autorizadas (Art. 35 LISR):
Edificios y construcciones: 5%
Ferrocarriles y barcos: 6%
Aviones (sin aerotaxi): 25%
Automóviles, autobuses, camiones: 25%
Computadoras y equipo de cómputo: 30%
Dados, troqueles, moldes, matrices: 35%
Comunicaciones telefónicas: 10%
Comunicaciones satelitales: 8%
Maquinaria industrial en general: 10%
Equipos de generación de energía: 10%
Instrumentos de medición: 10%
Herramientas y equipo de taller: 35%
Para Fourgea: filtros en arrendamiento/préstamo → 25% (equipo no identificado como maquinaria fija)
Para Triple R: tanques de almacenamiento → 5% (similar a construcción).
La depreciación fiscal puede diferir de la contable (CINIF NIF C-6).""",
"LISR Art. 34-40","depreciación fiscal 5% edificios 25% autos 30% cómputo 10% maquinaria tasa LISR",2026),

("isr","perdidas_fiscales","Pérdidas Fiscales — Amortización y Límites",
"""Las pérdidas fiscales (cuando deducciones > ingresos) se pueden amortizar contra utilidades futuras.
Reglas (Art. 57 LISR):
- Plazo: hasta 10 ejercicios siguientes
- Se actualiza por inflación (factor INPC) desde el primer mes de la segunda mitad del ejercicio que generó la pérdida hasta el último mes del ejercicio en que se aplica
- Tope: no hay límite de monto, pero no puede generar otra pérdida al aplicarla
- Si la empresa se fusiona o escinde: limitaciones especiales
Ejemplo: Fourgea tiene pérdida fiscal 2024 de $500,000 → puede restarla de utilidades 2025-2034
Al aplicar en 2026: actualización por inflación mejora el valor de la pérdida.""",
"LISR Art. 57-58","pérdida fiscal amortización 10 años actualización INPC fusión escisión",2026),

("isr","dividendos","Dividendos — Tratamiento Fiscal",
"""Distribución de dividendos de persona moral a socio:
Si el socio es PERSONA FÍSICA residente en México:
  - La PM retiene 10% del dividendo bruto (Art. 140 LISR)
  - El dividendo es ingreso acumulable para la PF en su declaración anual
  - La PM ya pagó 30% ISR sobre la utilidad, entonces el total efectivo es ~37%
Si el socio es PERSONA MORAL residente en México: dividendo no acumulable (evita doble imposición).
Si el socio es RESIDENTE EN EL EXTRANJERO: retención 10% (o tasa del tratado).
CUFIN (Cuenta de Utilidad Fiscal Neta): dividendo que sale de CUFIN no paga ISR adicional.
Si el dividendo sale de utilidades NO en CUFIN: PM paga ISR corporativo adicional (piramidación).""",
"LISR Art. 10, 77, 140","dividendos CUFIN retención 10% persona física socio extranjero piramidación",2026),

# ═══════════════════════════════════════════════════════════════════
# R. INFRACCIONES Y SANCIONES ADUANALES Y FISCALES
# ═══════════════════════════════════════════════════════════════════

("aduanas","infracciones","Infracciones Aduanales Comunes y Multas 2026",
"""Infracciones frecuentes en importación y sus multas (LA Art. 176-199):
1. FRACCIÓN ARANCELARIA INCORRECTA: multa del 70% al 100% del IGI omitido.
2. VALOR EN ADUANA INCORRECTO: multa 130% del impuesto omitido si hay dolo, 70% si es error.
3. DOCUMENTACIÓN FALSA: penalización penal (contrabando) hasta 9 años de prisión.
4. NO PRESENTAR MVE: multa $4,000 a $8,000 pesos.
5. EXCEDER TIEMPO DE IMPORTACIÓN TEMPORAL (IMMEX): pagar IGI + IVA + recargos + multa 70%.
6. NO RETORNAR MERCANCÍA TEMPORAL: considérase importación definitiva no declarada.
7. TRANSPORTAR SIN CARTA PORTE: retención de mercancía + multa $4,000-$16,000.
RECONOCIMIENTO ADUANERO: si la aduana detecta error en físico vs. factura, inicia procedimiento administrativo (PAMA).
Prescripción: 5 años para que el SAT reclame créditos aduanales.""",
"LA Art. 176-199, CFF Art. 146","infracciones multas importación fracción arancelaria PAMA carta porte MVE contrabando",2026),

("sat","infracciones_fiscales","Infracciones Fiscales Comunes — CFF",
"""Infracciones y multas más frecuentes del CFF 2026:
NO EMITIR CFDI:
  - 1ra vez: $1,330 a $3,990 por comprobante no emitido
  - Reincidencia: clausura de 3-15 días
NO PRESENTAR DECLARACIÓN A TIEMPO:
  - $1,400 a $17,370 por declaración (+ recargos sobre saldo)
LLEVAR CONTABILIDAD INCORRECTA:
  - $230 a $4,170 por cada libro o registro
NO INSCRIBIRSE EN RFC:
  - Persona moral: $5,230 a $17,580
PRESENTAR DECLARACIÓN CON DATOS ERRÓNEOS:
  - 55% a 75% de contribución omitida (con dolo 100%-150%)
RECARGOS: tasa mensual publicada en RMF (~1.47% mensual en 2026 sobre saldo histórico actualizado).
ACTUALIZACIÓN: INPC entre mes de vencimiento y mes de pago.""",
"CFF Art. 76-91","multas CFDI declaración recargos actualización INPC infracciones fiscales 2026",2026),

("sat","revision_electronica","Revisión Electrónica SAT — Carta Invitación",
"""El SAT puede iniciar revisiones sin ir físicamente a la empresa:
1. CARTA INVITACIÓN: correo o notificación en buzón tributario solicitando aclaraciones.
   - Plazo para aclarar: 15 a 30 días
   - No es una auditoría formal, pero puede derivar en una
2. REVISIÓN ELECTRÓNICA: auditoría basada en datos del SAT (CFDI, declaraciones, pedimentos).
   - Pre-liquidación: el SAT muestra monto supuesto y da 20 días para aclarar
   - Si no se aclara: crédito fiscal determinado
3. AUDITORÍA EN GABINETE: requerimiento de papeles de trabajo en las oficinas del SAT.
4. VISITA DOMICILIARIA: auditores van a las instalaciones (cada vez menos frecuente).
Para Fourgea/Triple R: la mayoría de discrepancias detectadas son por:
- CFDI emitido vs. declaración (diferencias de IVA)
- Pedimentos vs. deducciones de importación reportadas""",
"CFF Art. 42-46","revisión electrónica SAT carta invitación pre-liquidación auditoría CFDI pedimentos",2026),

# ═══════════════════════════════════════════════════════════════════
# S. RFC, CSD Y SELLOS DIGITALES
# ═══════════════════════════════════════════════════════════════════

("sat","rfc","RFC y e.firma — Obligaciones Iniciales",
"""RFC (Registro Federal de Contribuyentes):
Fourgea Mexico SA de CV: RFC E080820LC2
Triple R Oil México: RFC O150504GE3
Para obtener o actualizar RFC:
  - Personas morales: acta constitutiva + poderes del representante legal + ID
  - Personas físicas: CURP + ID oficial
e.firma (antes FIEL): certificado digital personal del representante legal.
  - Vigencia: 4 años
  - Renovar en SAT antes del vencimiento (con e.firma vigente)
  - Sin e.firma: no se puede firmar declaraciones, solicitar devoluciones ni acceder a Buzón Tributario
CSD (Certificado de Sello Digital): para timbrar CFDI 4.0.
  - Vigencia: 4 años (puede ser diferente a e.firma)
  - Una empresa puede tener múltiples CSD (para distintos establecimientos)
  - Si el SAT cancela el CSD (efecto de embargo o incumplimiento): no se puede emitir CFDI""",
"CFF Art. 17-D, 27","RFC e.firma CSD certificado sello digital vigencia 4 años timbrar CFDI buzón tributario",2026),

("sat","buzon_tributario","Buzón Tributario SAT — Notificaciones Electrónicas",
"""El Buzón Tributario es el canal oficial del SAT para comunicarse con el contribuyente.
Obligatorio para personas morales desde 2014, personas físicas desde 2015.
Funciones:
- Recibir notificaciones oficiales (créditos, requerimientos, resoluciones)
- Presentar promociones y trámites
- Recibir resoluciones del SAT
IMPORTANTE: las notificaciones en buzón tienen efectos legales desde que el contribuyente las abre O a los 3 días de enviadas (lo que ocurra primero).
Si no se revisa el buzón → los plazos corren igual → preclusión de derechos.
Para Fourgea: revisar el buzón tributario al menos cada semana para no perder plazos.
Correo de alerta: configurar en portal SAT para recibir aviso por email cuando llega notificación.""",
"CFF Art. 17-K","buzón tributario notificación electrónica 3 días plazo preclusión derechos SAT",2026),

# ═══════════════════════════════════════════════════════════════════
# T. EXPORTACIÓN — ASPECTOS FISCALES
# ═══════════════════════════════════════════════════════════════════

("comercio_exterior","exportacion_iva","IVA en Exportaciones — Tasa 0% y Devolución",
"""Las exportaciones definitivas de bienes tangibles están gravadas a tasa 0% de IVA (Art. 29 LIVA).
Esto significa:
- No se cobra IVA al cliente extranjero
- Pero sí se acredita TODO el IVA pagado en México para producir/adquirir lo exportado
- Resultado: generalmente saldo a favor de IVA que se puede devolver
Documentación para comprobar exportación:
  1. Pedimento de exportación G1 validado por aduana
  2. Factura comercial al cliente extranjero (con datos completos del receptor)
  3. Comprobante de embarque (BL, guía aérea o carta porte)
Si Triple R exporta aceites → paga IVA 0%, puede pedir devolución del IVA de sus insumos.
Plazo SAT devolución IVA exportadores: 20 días hábiles (automática) o 5 días con certificación IVA/IEPS.""",
"LIVA Art. 29-32","IVA exportación 0% devolución saldo favor pedimento G1 certificación acreditamiento",2026),

("comercio_exterior","pedimento_exportacion","Pedimento de Exportación — Proceso",
"""Proceso para exportar mercancía de México:
1. El exportador o agente aduanal clasifica la mercancía en TIGIE y determina fracción de exportación.
2. Se elabora el pedimento G1 (exportación definitiva) o V5 (temporal).
3. Se pagan derechos si aplican (generalmente 0% para exportaciones manufactureras).
4. El SAT puede solicitar reconocimiento aduanero o la mercancía sale sin revisión (desaduanamiento).
5. La aduana valida el pedimento y se genera el número de pedimento oficial.
6. El transportista recibe la mercancía ya con el pedimento pagado.
Documentos que el exportador (Triple R o Fourgea) da al agente:
  - Factura comercial al cliente extranjero (en USD o la moneda del contrato)
  - Packing list
  - Certificado de origen T-MEC si aplica
  - Permisos de exportación si los hay (algunos productos químicos los requieren)""",
"LA Art. 96-98","pedimento exportación G1 V5 proceso agente aduanal fracción TIGIE certificado origen",2026),

# ═══════════════════════════════════════════════════════════════════
# U. FINANCIAMIENTO Y CRÉDITO FISCAL
# ═══════════════════════════════════════════════════════════════════

("sat","compensacion","Compensación y Devolución de Saldos a Favor",
"""Cuando hay saldo a favor en declaraciones, el contribuyente puede:
1. COMPENSACIÓN UNIVERSAL (hasta 2019): compensar contra cualquier impuesto federal — eliminada.
2. COMPENSACIÓN ACTUAL: solo contra el mismo impuesto (IVA vs IVA, ISR vs ISR) o retenciones del mismo período.
   Excepción: el IVA de exportaciones sí puede pedirse en devolución directa.
3. DEVOLUCIÓN: solicitud formal en portal SAT.
   - IVA: 20 días hábiles automática / 40 días normal
   - ISR (saldo a favor declaración anual): 25 días hábiles
   - Exportadores con certificación IVA/IEPS: 5 días hábiles
Requisitos para devolución:
  - Tener e.firma vigente
  - RFC al corriente de obligaciones (sin adeudos ni incumplimientos)
  - Cuenta CLABE bancaria registrada en SAT
Fourgea: puede tener saldo a favor de IVA en meses con muchas importaciones vs. pocas ventas.""",
"CFF Art. 22-23, LIVA Art. 6","saldo favor devolución compensación IVA ISR 20 días 40 días CLABE exportadores",2026),

("sat","facilidades_pago","Facilidades de Pago — Pago en Parcialidades",
"""Si se tiene adeudo fiscal, se puede pagar en parcialidades (Art. 66 CFF):
Plazos máximos:
  - Hasta 12 meses: sin garantía adicional
  - 13 a 36 meses: se requiere garantía (fianza, hipoteca, prenda)
Tasa de interés: TIIE a 28 días + 2 puntos (aproximadamente 13-15% anual en 2026).
También existe la PRÓRROGA: aplazar una sola fecha de pago (máximo 12 meses adicionales).
Condonación: el SAT emite periódicamente programas de condonación de multas (pero no de contribuciones).
En trámites aduanales: el importador puede otorgar garantía para desaduanar mercancía en disputa sin pagar el crédito fiscal inmediatamente.""",
"CFF Art. 66-66-A","pago parcialidades adeudo fiscal TIIE 36 meses garantía prorroga condonación multas",2026),

# ═══════════════════════════════════════════════════════════════════
# V. OPERADOR ECONÓMICO AUTORIZADO (OEA)
# ═══════════════════════════════════════════════════════════════════

("aduanas","oea","OEA — Operador Económico Autorizado",
"""El OEA es una certificación del SAT para importadores/exportadores confiables que agiliza el despacho aduanal.
Beneficios:
- Carril exclusivo en aduana (despacho más rápido)
- Menor frecuencia de reconocimientos físicos
- Acceso a regímenes especiales simplificados
- Coordinación con otros países (reconocimiento mutuo EEUU, UE, etc.)
Modalidades:
  - Tipo A: importadores/exportadores
  - Tipo B: agentes aduanales
  - Tipo C: transportistas
  - Tipo D: recinteros
Requisitos generales:
  1. RFC activo y corriente de obligaciones
  2. No haber tenido créditos fiscales relevantes en los últimos 3 años
  3. Sistema de control de inventarios certificado
  4. Capacitación en seguridad de la cadena de suministro
Para Fourgea: obtener OEA tipo A reduciría costos operativos de importación significativamente.""",
"LA Art. 100-A, Reglas RGCE","OEA operador económico autorizado certificación importador despacho ágil reconocimiento",2026),

# ═══════════════════════════════════════════════════════════════════
# W. IVA ACREDITABLE — REGLAS ESPECIALES
# ═══════════════════════════════════════════════════════════════════

("iva","acreditamiento","IVA Acreditable — Requisitos para Acreditar",
"""Para acreditar IVA pagado, se deben cumplir TODOS estos requisitos (Art. 5 LIVA):
1. Que el IVA corresponda a bienes/servicios ESTRICTAMENTE INDISPENSABLES para la actividad gravada.
2. Que el gasto sea deducible para ISR (si no es deducible ISR, el IVA tampoco es acreditable).
3. Que se pague en el período (flujo de efectivo).
4. Que se tenga CFDI con los requisitos del Art. 29-A CFF (RFC del receptor, domicilio, régimen).
5. Si aplica, que el IVA haya sido retenido y enterado.
Excepciones:
- Vehículos cuyo deducible de ISR es limitado (sedan <$175,000) → IVA acreditable proporcional
- Gastos que generan actividades exentas → no acreditable
- Gastos mixtos (actividades gravadas y exentas) → proporcional al porcentaje de actividad gravada
Para Fourgea: todos los filtros que compra para revender están en actividad gravada → 100% acreditable.""",
"LIVA Art. 5","IVA acreditable requisitos indispensable deducible CFDI RFC proporcional actividad gravada exenta",2026),

("iva","retencion_iva","Retenciones de IVA — Cuándo y Cuánto",
"""Personas obligadas a RETENER IVA (Art. 1-A LIVA):
1. Personas morales que reciben servicios de personas físicas.
2. Personas físicas o morales que reciben servicios de comisión, mediación, agencia, etc.
3. Personas morales del sector financiero.
4. Personas morales que adquieren desperdicios.
MONTOS DE RETENCIÓN:
- Servicios personales independientes (honorarios, comisiones): retener 2/3 del IVA.
- Servicios de autotransporte terrestre: retener 4% del valor de la contraprestación.
- Servicios de personal temporal (outsourcing): retener 6%.
Obligación: enterar el IVA retenido el día 17 del mes siguiente.
En DIOT: reportar el IVA retenido en la columna correspondiente.
En CFDI: el prestador emite el CFDI indicando el IVA retenido; el receptor emite CFDI de retenciones.""",
"LIVA Art. 1-A, 3","retención IVA 2/3 honorarios autotransporte 4% outsourcing 6% persona moral física enterar",2026),

# ═══════════════════════════════════════════════════════════════════
# X. CONTABILIDAD DE COSTOS — IMPORTADOR COMERCIALIZADOR
# ═══════════════════════════════════════════════════════════════════

("contabilidad","costo_ventas","Costo de Ventas para Importador-Comercializador",
"""Para Fourgea (importa filtros y los revende sin transformación):
MÉTODO DE VALUACIÓN DE INVENTARIOS (Art. 41 LISR):
Método autorizado para personas morales:
  - PEPS (Primeras Entradas-Primeras Salidas): el más común para bienes no perecederos
  - Costo de identificación específica: para bienes de alto valor unitario
  - Costo promedio: simple de implementar, promedia todos los lotes
El método elegido no puede cambiarse sin autorización del SAT.
CÁLCULO DEL COSTO DE IMPORTACIÓN:
  Costo unitario = (Valor factura extranjero + IGI + DTA proporcional + flete nacional + seguro + agente aduanal) / unidades importadas
  Ejemplo: 1,000 filtros, valor aduana $200,000, IGI $10,000, DTA $669, flete nacional $3,000, agente $4,000
  Costo total = $217,669 / 1,000 = $217.67 por filtro
Al vender: Costo de venta = unidades vendidas × $217.67""",
"LISR Art. 39-41, CINIF NIF C-4","costo ventas importador inventarios PEPS promedio valuación costo importación unitario",2026),

("contabilidad","cuentas_orden","Cuentas de Orden y Conciliación Bancaria",
"""CONCILIACIÓN BANCARIA:
Diferencias entre estado de cuenta bancario y libro de bancos (causas normales):
1. Cheques en tránsito: emitidos pero no cobrados aún
2. Depósitos en tránsito: registrados contablemente pero no reflejados en banco
3. Cargos bancarios no registrados: comisiones, intereses, cargos automáticos
4. Errores: diferencias a investigar
Frecuencia: mensual (obligatoria para contabilidad electrónica SAT).
CUENTAS DE ORDEN: registros fuera del balance para control interno:
  - Mercancías en consignación
  - Garantías otorgadas
  - Bienes en arrendamiento
  - Pedimentos abiertos pendientes de pago
Para Fourgea: llevar cuenta de orden con pedimentos en proceso para controlar el inventario en tránsito.""",
"CINIF NIF B-10","conciliación bancaria cheques tránsito cargos bancarios cuentas orden pedimentos",2026),

# ═══════════════════════════════════════════════════════════════════
# Y. TIPO DE CAMBIO Y OPERACIONES EN MONEDA EXTRANJERA
# ═══════════════════════════════════════════════════════════════════

("contabilidad","tipo_cambio","Tipo de Cambio — Contabilización de Operaciones en USD",
"""Para registrar operaciones en moneda extranjera (Art. 20 CFF y CINIF NIF B-15):
TIPO DE CAMBIO FISCAL: publicado diariamente por el Banco de México (Banxico) en el DOF.
  - Para pedimentos: tipo de cambio del día anterior al del despacho aduanal.
  - Para CFDI en USD: tipo de cambio del día de emisión del CFDI.
  - Para pagos al extranjero: tipo de cambio del día del pago.
FLUCTUACIÓN CAMBIARIA:
  - Cuando el USD sube vs MXN: la deuda con el proveedor extranjero (en pesos) aumenta → pérdida cambiaria (gasto deducible ISR).
  - Cuando el USD baja: ganancia cambiaria (ingreso acumulable ISR).
  - Reconocer al cierre mensual la diferencia entre TC histórico y TC al cierre.
EJEMPLO: Fourgea debe $10,000 USD al proveedor.
  TC compra: $17.50 → deuda registrada $175,000 MXN
  TC al cierre del mes: $17.80 → deuda actualizada $178,000 MXN
  Pérdida cambiaria reconocida: $3,000 MXN (deducible ISR)""",
"CFF Art. 20, CINIF NIF B-15","tipo cambio Banxico DOF fluctuación cambiaria pérdida ganancia USD deuda proveedor",2026),

("contabilidad","pagos_exterior","Pagos al Exterior — SWIFT y Obligaciones Fiscales",
"""Al pagar a proveedor extranjero en USD o EUR:
1. RETENCIÓN ISR si el pago es por servicios (no por bienes importados).
2. DECLARACIÓN A-29 (DIOT): reportar el pago al proveedor extranjero.
3. ANTI-LAVADO: transferencias >$10,000 USD se reportan al SAT (Art. 17 Ley Anti-Lavado).
   Transferencias >$3,000 USD pueden requerir identificación adicional en el banco.
4. TIPO DE CAMBIO: usar TC Banxico del día del pago para convertir a MXN en contabilidad.
5. Bancos mexicanos a veces solicitan factura del proveedor para liberar transferencias internacionales.
Para Triple R (aceites de EEUU): generalmente pago en USD por SWIFT, sin retención si es compra de mercancía.
Contrato de compra-venta internacional recomendado para soportar la operación ante el SAT.""",
"CFF Art. 32-B, Ley Anti-Lavado","pago exterior SWIFT USD anti-lavado $10,000 reporte DIOT proveedor extranjero",2026),

# ═══════════════════════════════════════════════════════════════════
# Z. NIF/CINIF — NORMAS DE INFORMACIÓN FINANCIERA
# ═══════════════════════════════════════════════════════════════════

("contabilidad","nif_inventarios","NIF C-4 — Inventarios",
"""NIF C-4 establece el tratamiento contable de los inventarios:
VALUACIÓN AL MENOR ENTRE: costo de adquisición y valor neto de realización.
Métodos permitidos por NIF C-4:
  - PEPS (primero en entrar primero en salir)
  - Costo promedio ponderado
  - No se permite UEPS desde 2011
Deterioro de inventarios: si el valor neto de realización < costo → reconocer pérdida.
Casos que requieren ajuste:
  - Mercancías obsoletas (filtros que ya no tienen demanda)
  - Daños físicos en almacén
  - Reducción en precio de mercado
Para Fourgea: revisar inventario de filtros cada cierre de ejercicio. Los filtros dañados o sin salida deben registrarse a su valor neto de realización (precio de venta estimado - costos de disposición).""",
"CINIF NIF C-4","NIF inventarios PEPS promedio deterioro valor neto realización obsoleto daño ajuste",2026),

("contabilidad","nif_activo_fijo","NIF C-6 — Propiedades, Planta y Equipo",
"""NIF C-6 regula el activo fijo (propiedades, planta y equipo):
RECONOCIMIENTO INICIAL: al costo de adquisición (precio + importación + instalación + pruebas).
Para equipo importado: costo incluye valor aduana + IGI + DTA + flete nacional + instalación.
DEPRECIACIÓN CONTABLE: basada en vida útil estimada (puede diferir de tasas fiscales LISR).
  - Línea recta: cargo uniforme por vida útil estimada
  - Método de unidades de producción: según horas de uso
DIFERENCIA CONTABLE VS FISCAL:
  - Contable: depreciación según vida útil real (ej. computadora 5 años = 20%)
  - Fiscal LISR: tasa fija 30%
  - Diferencia = impuesto diferido (NIF D-4)
BAJA DE ACTIVO FIJO: cuando se vende o da de baja → reconocer utilidad o pérdida en venta.""",
"CINIF NIF C-6","NIF activo fijo propiedades planta equipo costo depreciación vida útil diferencia fiscal impuesto diferido",2026),

# ═══════════════════════════════════════════════════════════════════
# AA. ADUANAS — TIGIE CAPÍTULOS ADICIONALES
# ═══════════════════════════════════════════════════════════════════

("tigie","lubricantes_industriales","TIGIE — Aceites y Lubricantes para Maquinaria Industrial (Triple R)",
"""Fracciones arancelarias específicas para Triple R Oil México:
2710.19.02 — Aceites lubricantes acabados con aditivos antioxidantes: IGI libre
2710.19.03 — Aceites para transmisiones automáticas (ATF): IGI libre
2710.19.04 — Aceites para motores de dos tiempos: IGI libre
2710.19.05 — Aceites corte y taladrinas (metalurgia): IGI libre
2710.19.06 — Aceites hidráulicos minerales: IGI libre
2710.19.07 — Aceites para engranajes y cajas de velocidades: IGI libre
3403.11.01 — Lubricantes sólidos y semisólidos (grasas con base mineral): IGI libre
3403.19.99 — Las demás grasas lubricantes: IGI libre
Nota: todos los aceites de capítulo 27 tienen IGI libre (0%) para México incluyendo importaciones de China.
El único impuesto relevante es IVA 16%. No aplica IEPS para lubricantes (solo para combustibles).""",
"TIGIE SE Cap. 27, 34","TIGIE aceites lubricantes ATF hidráulicos corte grasas 2710 3403 IGI libre Triple R",2026),

("tigie","quimicos_industriales","TIGIE — Químicos y Solventes para Mantenimiento Industrial",
"""Fracciones para productos químicos de mantenimiento industrial (Fourgea):
2710.12.07 — Solventes minerales (thinner, nafta mineral): IGI 5%
2905.11.01 — Metanol (alcohol metílico): IGI 5%
3402.20.99 — Agentes de limpieza industrial a base de tensioactivos: IGI 5%
3814.00.99 — Mezclas disolventes y diluyentes: IGI 5%
3820.00.01 — Anticongelantes: IGI 5% (T-MEC 0%)
3824.99.99 — Preparaciones químicas industriales no clasificadas: IGI 5% general
Para productos SEMARNAT: los solventes halogenados requieren autorización previa (CFC/HCFC-134a).
Etiquetado: NOM-018-STPS-2015 para sustancias peligrosas (SGA/GHS): pictogramas, fichas de seguridad.""",
"TIGIE SE Cap. 27, 29, 38","TIGIE solventes químicos industriales limpieza anticongelante 2710 3402 3820 SEMARNAT NOM-018",2026),

("tigie","maquinaria_electrica","TIGIE — Motores y Equipo Eléctrico Industrial",
"""Fracciones eléctricas para equipos industriales (Fourgea sistemas de filtración):
8501.10.01 — Motores de corriente continua hasta 37.5 W: IGI 5%
8501.20.01 — Motores monofásicos 37.5W-750W: IGI 5%
8501.51.01 — Motores de CA trifásicos hasta 750W: IGI 5%
8501.52.01 — Motores de CA trifásicos más de 750W: IGI 5%
8536.50.99 — Interruptores, seccionadores: IGI 5%
8537.10.99 — Tableros de control eléctrico: IGI 5%
8543.70.99 — Máquinas eléctricas especializadas: IGI 5%
Regla de origen T-MEC para equipo eléctrico: generalmente CC (cambio de capítulo) o RVC 35-45%.
Si el motor es de China con componentes no T-MEC: paga 5% IGI (sin preferencia).""",
"TIGIE SE Cap. 85","TIGIE motores eléctricos trifásico CA CC tablero control 8501 8537 IGI 5% T-MEC",2026),

("tigie","sellos_empaques","TIGIE — Sellos, Empaques y Material de Empaque",
"""Fracciones para empaques y sellos usados en filtración industrial:
4002.19.99 — Hule sintético (caucho SBR, NBR para juntas): IGI 5%
4016.93.99 — Juntas y empaques de hule vulcanizado: IGI 5%
4016.95.99 — Otros artículos de hule inflables o con forma: IGI 5%
5911.90.99 — Tejidos técnicos (telas filtrantes, fieltros): IGI 5%
6909.19.99 — Artículos cerámicos de uso industrial (boquillas filtrantes): IGI 5%
7318.15.99 — Tornillos y pernos de acero (para ensamble de filtros): IGI 5%
7320.20.99 — Resortes helicoïdales de acero (para válvulas y filtros): IGI 5%
Nota: para todos estos materiales auxiliares, si son originarios de EEUU con certificado T-MEC: 0% IGI.""",
"TIGIE SE Cap. 40, 59, 69, 73","TIGIE hule juntas empaques telas filtrantes tornillos resortes 4016 5911 7318 7320 IGI 5%",2026),

# ═══════════════════════════════════════════════════════════════════
# BB. RÉGIMEN ADUANERO — ORIGEN NO PREFERENCIAL
# ═══════════════════════════════════════════════════════════════════

("comercio_exterior","china_importacion","Importación desde China — Consideraciones Especiales",
"""Importar desde China implica diferencias vs. EEUU (sin T-MEC):
ARANCELES: se aplica la tasa general de la TIGIE (sin preferencia).
  - Filtros 8421.29.99 desde China: IGI 5% (misma tasa, T-MEC no aplica)
  - Aceites 2710.x desde China: IGI libre (0%)
  - Maquinaria 84.xx: generalmente 5%
CUOTAS COMPENSATORIAS: el SE puede imponer cuotas adicionales anti-dumping o compensatorias sobre productos chinos específicos. Verificar siempre en el Diario Oficial.
  - Si hay cuota compensatoria en 8421.29.99 → se suma al IGI
PROVEEDOR CHINO: no puede emitir certificado T-MEC, solo certificado de origen general (Formulario A del SGP).
CALIDAD/NOM: verificar que el producto chino cumpla las mismas NOMs que el equivalente americano.
INCOTERM CIF Puerto Manzanillo: el más usado para importaciones desde China.""",
"LA, SE Resoluciones Antidumping","China importación cuota compensatoria antidumping incoterm CIF Manzanillo NOM origen general",2026),

("comercio_exterior","certificado_origen_general","Certificados de Origen — Tratados Comerciales México",
"""México tiene tratados comerciales con tasa 0% o reducida para:
T-MEC (EEUU, Canadá): 0% mayoría de productos manufacturados.
  - Certificado: declaración en factura (desde 2020)
TLC México-UE: 0% a reducida para productos de la Unión Europea.
  - Certificado: EUR.1 o declaración en factura para exportadores certificados REX
TLC México-Japón: reducciones escalonadas; muchos productos 0% ya.
  - Certificado: formulario japonés oficial
TLC México-Israel: 0% para la mayoría de bienes industriales.
ACE México-Chile, Colombia, Perú (Alianza Pacífico): 0% para casi todo.
Para productos fuera de tratado (China, India, Turquía): tasa general TIGIE.
IMPORTANTE: siempre verificar la Lista de Desgravación del tratado para el capítulo específico.""",
"SE Dirección General de Comercio Exterior","tratados comerciales T-MEC TLC UE Japón Israel Alianza Pacífico certificado origen EUR.1",2026),

# ═══════════════════════════════════════════════════════════════════
# CC. NÓMINA AVANZADA
# ═══════════════════════════════════════════════════════════════════

("isr","subsidio_empleo","Subsidio para el Empleo — Mecánica y Obligaciones",
"""El subsidio para el empleo reduce el ISR retenido a trabajadores de bajos ingresos.
Funciona: el patrón calcula el ISR según tarifa, luego aplica la tabla de subsidio al empleo.
Si subsidio > ISR calculado: el patrón ENTREGA la diferencia al trabajador (subsidio enterado).
El patrón lo recupera deduciéndolo de sus impuestos propios.
LÍMITE: aplica solo para ingresos mensualmente hasta $10,172.64 (tabla 2026).
OBLIGACIONES:
  1. Comparar anualmente si se debió otorgar subsidio (ajuste en declaración anual del trabajador)
  2. Llevar registro individual del subsidio entregado
  3. Reportarlo en el CFDI de nómina (campo "OtrosPagos" tipo 002)
Si el trabajador tiene dos empleos: solo UN patrón aplica el subsidio (el principal).""",
"LISR Art. Décimo del Decreto 11-dic-2013","subsidio empleo ISR retenido trabajador tabla $10,172 CFDI nómina campo 002 OtrosPagos",2026),

("imss","sbc_integracion_detalle","SBC — Integración Detallada para Aguinaldo y Vacaciones",
"""Integración precisa del SBC con prestaciones variables (Art. 27 LSS):
AGUINALDO: 15 días mínimo legales / 365 días × salario diario. Si la empresa da 30 días, se integran 30/365.
PRIMA VACACIONAL: días de vacaciones × 25% / 365. Ej: 6 días vac × 25% = 1.5 días / 365 × SD.
COMISIONES: promedio mensual = suma de comisiones del bimestre / días del bimestre.
HORAS EXTRA HABITUALES: si se pagan regularmente, se integran (promedio).
EJEMPLO (empleado $300/día, 15 días aguinaldo, 6 días vacaciones):
  Factor aguinaldo: 15/365 = 0.04109
  Factor prima vacacional: 6 × 0.25 / 365 = 0.00411
  SBC = $300 × (1 + 0.04109 + 0.00411) = $300 × 1.0452 = $313.56/día
  Tope: $313.56 < 25 SMGDF ($6,970) ✓""",
"LSS Art. 27-29","SBC integración aguinaldo factor prima vacacional comisiones horas extra cálculo",2026),

("imss","cfdi_nomina_complemento","Complemento de Nómina 1.2 — Campos Clave",
"""El Complemento de Nómina 1.2 del CFDI incluye:
CAMPOS OBLIGATORIOS:
  - TipoNomina: O (Ordinaria) o E (Extraordinaria)
  - FechaPago: fecha real del depósito al trabajador
  - FechaInicialPago / FechaFinalPago: período cubierto
  - TotalDeducciones / TotalPercepciones / TotalOtrosPagos
  - NumDiasPagados: días que cubre la nómina
DATOS DEL EMPLEADO: CURP, NSS, TipoContrato, TipoJornada, TipoRegimen (02=sueldos), NumEmpleado
PERCEPCIONES: clave SAT (001=sueldos, 002=gratificación, 003=horas extra, etc.)
DEDUCCIONES: clave SAT (001=ISR, 002=IMSS obrero, 003=crédito INFONAVIT, etc.)
OTROS PAGOS: 001=reintegro ISR, 002=subsidio para el empleo
El CFDI de nómina se timbra con el CSD de la empresa; el trabajador lo puede descargar del portal SAT.""",
"SAT Complemento Nómina 1.2, Regla RMF 3.12","CFDI nómina complemento 1.2 percepciones deducciones CURP NSS clave SAT TipoNomina",2026),

# ═══════════════════════════════════════════════════════════════════
# DD. CIERRE MENSUAL — PROCEDIMIENTO COMPLETO
# ═══════════════════════════════════════════════════════════════════

("contabilidad","cierre_mensual_proceso","Cierre Mensual Contable — Procedimiento Paso a Paso",
"""Procedimiento de cierre mensual para empresas importadoras (Fourgea, Triple R):
1. CONCILIAR BANCOS: comparar estados de cuenta vs. libro de bancos. Detectar diferencias.
2. REGISTRAR PEDIMENTOS: cada pedimento del mes → asiento de importación (inventario + IVA acreditable).
3. VERIFICAR CFDIS: confirmar que todos los CFDI emitidos y recibidos están registrados en contabilidad.
4. CALCULAR COSTO DE VENTAS: salidas del almacén × costo unitario de importación (PEPS o promedio).
5. DEPRECIAR ACTIVOS FIJOS: cargo mensual (tasa anual / 12 meses).
6. CALCULAR NÓMINA Y PROVISIONES: sueldo del mes + provisión aguinaldo (1/12 cada mes) + provisión vacaciones.
7. CALCULAR IVA NETO: IVA trasladado cobrado - IVA acreditable pagado (incluye IVA de pedimentos).
8. CALCULAR ISR PROVISIONAL: ingresos del mes × CU × 30%.
9. CALCULAR RETENCIONES: ISR nómina + IVA retenido a proveedores personas físicas.
10. EMITIR BALANZA DE COMPROBACIÓN: verificar que débitos = créditos.
11. SUBIR BALANZA AL SAT: portal del SAT, a más tardar día 25 del mes siguiente.""",
"CFF Art. 28, LISR Art. 14","cierre mensual procedimiento importación conciliación bancos pedimentos IVA ISR balanza SAT",2026),

("contabilidad","provision_aguinaldo","Provisión de Aguinaldo — Registro Mensual",
"""Para distribuir el costo del aguinaldo uniformemente durante el año:
Cálculo mensual de la provisión:
  Provisión mensual por empleado = (Salario mensual × días aguinaldo) / 12 meses
  Ejemplo: empleado $20,000/mes, 15 días aguinaldo:
    Días aguinaldo = 15 días × ($20,000/30 días) = $10,000 anual
    Provisión mensual = $10,000 / 12 = $833.33/mes
ASIENTO:
  DEBE: 601 Gastos de administración (aguinaldo) .... $833.33
  HABER: 215 Provisión aguinaldo por pagar .......... $833.33
Al pagar en diciembre:
  DEBE: 215 Provisión aguinaldo ..................... $10,000
  HABER: 102 Bancos ................................. $10,000
Fiscalmente: el aguinaldo pagado es deducible ISR en el ejercicio en que se paga (no cuando se provisiona).""",
"CINIF NIF D-3","provisión aguinaldo mensual ISR deducible diciembre asiento contable empleado",2026),

# ═══════════════════════════════════════════════════════════════════
# EE. EXPORTACIÓN DE SERVICIOS
# ═══════════════════════════════════════════════════════════════════

("iva","servicios_exportacion","IVA en Exportación de Servicios",
"""Los servicios se consideran exportados (tasa 0%) cuando son aprovechados en el extranjero (Art. 29 fracc. IV LIVA):
Ejemplos de servicios gravados a 0% IVA:
  - Asistencia técnica a empresas extranjeras pagada desde el extranjero
  - Servicios de diseño o ingeniería contratados por empresa del extranjero
  - Servicios de call center para clientes en el extranjero
Para comprobar exportación de servicio:
  1. Contrato con la empresa extranjera
  2. Factura en moneda extranjera (o con cláusula de pago en el extranjero)
  3. Transferencia SWIFT recibida del extranjero
Si Sonora Digital Corp presta servicios de IA/software a empresas fuera de México: aplica tasa 0%, con derecho a devolución de IVA pagado en costos.
Si el servicio se aprovecha en México (aunque el cliente sea extranjero): tasa 16%.""",
"LIVA Art. 29 fracc. IV","IVA 0% exportación servicios aprovechados extranjero contrato SWIFT IA software",2026),

# ═══════════════════════════════════════════════════════════════════
# FF. DICTAMEN FISCAL / ISSIF
# ═══════════════════════════════════════════════════════════════════

("sat","dictamen_issif","ISSIF — Informe Sobre Situación Fiscal (antes Dictamen Fiscal)",
"""El ISSIF (Art. 32-A CFF) sustituyó al Dictamen Fiscal tradicional.
OBLIGADOS a presentar ISSIF (si en el ejercicio anterior):
  - Ingresos > $1,650,490,600 (actualizado 2026)
  - Acciones colocadas en bolsa
  - Personas morales residentes en el extranjero con establecimiento permanente
OPTATIVO para los demás contribuyentes.
QUIÉN LO ELABORA: Contador Público Registrado (CPR) autorizado por el SAT.
PLAZO: junto con la declaración anual (31 marzo para PM, 30 abril para PF).
BENEFICIOS al presentar ISSIF:
  - Los saldos a favor se devuelven más rápido
  - Menor probabilidad de auditoría directa
Para Fourgea y Triple R (con ingresos < $1,650 millones): el ISSIF es opcional pero recomendable si quieren agilizar devoluciones.""",
"CFF Art. 32-A","ISSIF dictamen fiscal CPR contador público registrado declaración anual devolución auditoría",2026),

# ═══════════════════════════════════════════════════════════════════
# GG. OBLIGACIONES INFORMATIVAS ESPECIALES
# ═══════════════════════════════════════════════════════════════════

("sat","declaraciones_informativas","Declaraciones Informativas — Obligaciones Anuales",
"""Declaraciones informativas que deben presentar personas morales importadoras:
1. DIM (Declaración Informativa Múltiple) — Febrero:
   Anexo 1: sueldos y salarios pagados
   Anexo 2: honorarios a personas físicas
   Anexo 3: arrendamiento pagado a personas físicas
   Anexo 9: partes relacionadas (precios de transferencia)
2. INFORMACIÓN DE PRÉSTAMOS, APORTACIONES Y DIVIDENDOS (Art. 76 LISR) — Febrero:
   Dividendos pagados a extranjeros y residentes en México
3. CONTABILIDAD ELECTRÓNICA (Balanza anual) — Marzo
4. OPERACIONES CON PARTES RELACIONADAS RESIDENTES EN EL EXTRANJERO — Diciembre 31
5. ICSOE (Información sobre Situación Fiscal para ciertas empresas) — Diciembre 31
Para Fourgea/Triple R: principalmente DIM Anexo 1 (nómina), Anexo 9 si hay operaciones entre ellas, y contabilidad electrónica mensual.""",
"CFF Art. 32, LISR Art. 76","declaraciones informativas DIM anexo nómina honorarios partes relacionadas contabilidad electrónica",2026),

("sat","obligaciones_importador","Obligaciones Registrales del Importador",
"""Todo importador habitual debe estar registrado en:
1. RFC ACTIVO: con actividad de importación declarada.
2. PADRÓN DE IMPORTADORES (SAT): obligatorio para importar cualquier mercancía.
   - Solicitud en portal SAT con RFC, domicilio fiscal verificado, representante legal
   - Se puede solicitar la suspensión temporal si se deja de importar
3. PADRÓN DE IMPORTADORES DE SECTORES ESPECÍFICOS: para mercancías de alto riesgo (textiles, calzado, electrónicos, químicos, siderúrgicos).
   - Fourgea: si importa filtros con componentes electrónicos → verificar si aplica sector específico
   - Triple R: aceites generalmente no requieren sector específico
4. REGISTRO DE EMPRESAS CERTIFICADAS: si se obtiene OEA o se opera bajo IMMEX.
Si se cancela el padrón → no se puede importar hasta rehabilitación.""",
"LA Art. 59-E, RGCE","padrón importadores SAT registro sectores específicos OEA IMMEX RFC activo",2026),

# ═══════════════════════════════════════════════════════════════════
# HH. OPERACIONES ESPECÍFICAS FOURGEA Y TRIPLE R
# ═══════════════════════════════════════════════════════════════════

("comercio_exterior","fourgea_proceso","Proceso de Importación Típico Fourgea Mexico",
"""Flujo completo de una importación de filtros para Fourgea Mexico SA de CV (RFC: E080820LC2):
1. NEGOCIACIÓN: acuerdo con proveedor en EEUU/China (precio FOB/CIF, tiempo de entrega, incoterm).
2. ORDEN DE COMPRA: emisión de PO con detalle de productos (modelo, cantidad, precio).
3. EMBARQUE: proveedor envía con BL marítimo o AWB aéreo + factura comercial + packing list + certificado de origen (si T-MEC).
4. AVISO AL AGENTE ADUANAL: enviar documentos al agente para preparar pedimento.
5. PAGO DE IMPUESTOS: agente calcula valor en aduana, IGI, DTA, IVA y paga electrónicamente.
6. DESPACHO ADUANAL: aduana libera la mercancía (semáforo: verde=pasa, rojo=revisión física).
7. TRANSPORTE NACIONAL: mercancía llega al almacén Fourgea con carta porte.
8. RECEPCIÓN EN ALMACÉN: verificar vs. packing list, registrar en sistema (entrada a inventario).
9. REGISTRO CONTABLE: asiento de importación (inventario + IVA acreditable + cuentas por pagar).
10. PAGO AL PROVEEDOR: 30-60 días después por SWIFT.
Tiempo total estimado: embarque marítimo EEUU → México: 10-15 días; aéreo: 3-5 días.""",
"LA, INCOTERMS 2020","Fourgea importación proceso pedimento despacho aduanal inventario agente carta porte",2026),

("comercio_exterior","triple_r_proceso","Proceso de Importación Típico Triple R Oil México",
"""Flujo de importación de aceites lubricantes para Triple R Oil México (RFC: O150504GE3):
PROVEEDOR TÍPICO: refinerías en EEUU o distribuidores de lubricantes.
FRACCIÓN ARANCELARIA: 2710.19.xx (aceites lubricantes) — IGI libre, IVA 16%.
INCOTERM: FOB Houston o CIF Laredo (por tierra).
TRANSPORTE: autotransporte terrestre EEUU-México (cruce por Laredo o Nogales generalmente).
DOCUMENTOS ESPECIALES PARA ACEITES:
  - Ficha técnica del aceite (especificaciones técnicas, viscosidad, grado API)
  - Certificado de análisis de composición (del fabricante)
  - Safety Data Sheet (SDS/MSDS) — cumplimiento NOM-018-STPS
PERMISOS:
  - No requiere permiso SEMARNAT para aceites lubricantes vírgenes
  - Si son aceites usados o reciclados: SÍ requiere autorización ambiental
TIEMPO ESTIMADO: cruce terrestre 1-2 días (más rápido que marítimo).""",
"LA, NOM-018-STPS","Triple R aceites importación terrestre Laredo Nogales SDS ficha técnica API",2026),

("contabilidad","fourgea_cfdi_ventas","CFDI de Ventas Fourgea — Configuración Correcta",
"""Para emitir CFDI de venta de filtros industriales (Fourgea):
DATOS OBLIGATORIOS CFDI 4.0:
  - Emisor: Fourgea Mexico SA de CV | RFC: E080820LC2
  - Régimen fiscal emisor: 601 (General de Ley Personas Morales)
  - Receptor: RFC del cliente, nombre completo según SAT, domicilio fiscal
  - Régimen fiscal del receptor (según catálogo SAT)
  - Uso del CFDI del receptor (catálogo: G03=Gastos en general, G01=Adquisición bienes)
  - Descripción del producto: "Filtro industrial modelo XX — uso en maquinaria"
  - Fracción arancelaria en CFDI: 8421.29.99 (si se vende a importador o exportador)
  - Objeto de impuesto: 02 (Sí objeto de impuesto)
  - IVA trasladado: 16% sobre el precio neto
FORMA DE PAGO: PUE (pago en una sola exhibición si se paga en el mes) o PPD + Complemento de Pago.
Si se paga a 30 días: emitir CFDI con método de pago PPD y después emitir complemento de pago.""",
"CFF Art. 29-A, SAT CFDI 4.0","CFDI ventas Fourgea filtros 8421 régimen 601 receptor uso G03 G01 PPD complemento pago",2026),

# ═══════════════════════════════════════════════════════════════════
# II. DECLARACIÓN ANUAL ISR PERSONAS MORALES — DETALLE
# ═══════════════════════════════════════════════════════════════════

("isr","declaracion_anual_pm","Declaración Anual ISR Personas Morales — Procedimiento",
"""Presentar declaración anual ISR personas morales (plazo: 31 marzo):
HERRAMIENTA: Portal SAT — DEM (Declaración de Personas Morales).
DATOS NECESARIOS:
  1. Ingresos acumulables totales del ejercicio
  2. Deducciones autorizadas (costo de ventas, gastos, depreciaciones)
  3. Participación de los Trabajadores en las Utilidades (PTU) pagada
  4. Pagos provisionales realizados (ISR mensual acumulado)
  5. Retenciones que clientes le efectuaron (si aplica)
  6. Créditos fiscales (si hay pérdidas de ejercicios anteriores actualizadas)
CÁLCULO:
  Ingresos - Deducciones = Utilidad bruta fiscal
  Utilidad bruta - PTU = Utilidad fiscal
  Utilidad fiscal × 30% = ISR del ejercicio
  ISR ejercicio - Pagos provisionales - Retenciones = ISR a cargo (o saldo a favor)
Si hay SALDO A FAVOR: puede pedirse en devolución o compensarse con declaraciones futuras.
ERRORES COMUNES: no incluir todos los ingresos, no deducir gastos por falta de CFDI.""",
"LISR Art. 9, CFF Art. 32","declaración anual personas morales ISR marzo DEM ingresos deducciones PTU pagos provisionales",2026),

("isr","cufin_cuca","CUFIN y CUCA — Cuentas de Capital Fiscal",
"""Cuentas de capital fiscal que toda persona moral debe llevar:
CUFIN (Cuenta de Utilidad Fiscal Neta — Art. 77 LISR):
  + Utilidades fiscales netas (después de ISR)
  - Dividendos distribuidos
  Cuando se distribuye dividendo desde CUFIN: no se paga ISR adicional.
  Cuando se distribuye dividendo fuera de CUFIN: la empresa paga ISR (30% piramidado = 42.86% sobre el dividendo).
CUCA (Cuenta de Capital de Aportación — Art. 78 LISR):
  Registra las aportaciones de los socios.
  Cuando se devuelven aportaciones (reducción de capital): hasta el saldo de CUCA no paga ISR.
  El excedente sobre CUCA se trata como dividendo.
Para Fourgea: llevar CUFIN actualizada con inflación (factor INPC anual) para distribuir utilidades sin costo fiscal adicional.""",
"LISR Art. 77-78","CUFIN CUCA utilidad fiscal neta capital aportación dividendo ISR piramidación reducción capital",2026),

# ═══════════════════════════════════════════════════════════════════
# JJ. COMERCIO ELECTRÓNICO Y PLATAFORMAS DIGITALES
# ═══════════════════════════════════════════════════════════════════

("iva","plataformas_digitales","IVA en Plataformas Digitales y Marketplace",
"""Desde 2020, las plataformas digitales retienen y entiran el IVA de las transacciones:
OBLIGADAS A RETENER: Amazon, MercadoLibre, Shopify, Google, Uber, etc.
  - Para personas físicas que venden en la plataforma: retención del 50% del IVA.
  - Para personas morales (Fourgea, Triple R vendiendo en Amazon): la PM paga su propio IVA.
REGLAS 2026:
  Si Fourgea vende filtros en Amazon México:
  - Fourgea emite CFDI y declara el IVA completo (Amazon no retiene a personas morales).
  - Si vende exportando via Amazon FBA a clientes en EEUU: IVA 0%.
Para servicios digitales del extranjero (Google Ads, Microsoft, HubSpot):
  - El proveedor extranjero está obligado a registrarse ante el SAT y cobrar IVA 16%.
  - Fourgea paga el IVA incluido en el servicio; puede acreditarlo si tiene CFDI.""",
"LIVA Art. 18-D, 18-J","IVA plataformas digitales Amazon marketplace retención Google Microsoft CFDI extranjero",2026),

# ═══════════════════════════════════════════════════════════════════
# KK. AUDITORÍA INTERNA Y CONTROL
# ═══════════════════════════════════════════════════════════════════

("contabilidad","control_interno_importador","Control Interno para Importadores — Mejores Prácticas",
"""Controles internos recomendados para Fourgea y Triple R como importadoras:
1. AUTORIZACIÓN DE COMPRAS: toda orden de compra al extranjero requiere firma del gerente.
2. EXPEDIENTE DE PEDIMENTO: conservar digitalmente (5 años): pedimento, factura, BL, packing list, MVE, certificado origen, CFDI de gastos.
3. CONCILIACIÓN MENSUAL: comparar pedimentos importados vs. entradas al almacén vs. registro contable.
4. VERIFICACIÓN DE FRACCIONES: revisar anualmente si la fracción usada sigue siendo correcta (el SAT actualiza la TIGIE).
5. ACTUALIZACIÓN DE PROVEEDORES: verificar que los proveedores extranjeros sigan activos y que los precios sean de mercado (precios de transferencia si son relacionados).
6. CONTROL DE PEDIMENTOS ABIERTOS: llevar registro de mercancías en tránsito aún no despachadas.
7. CUMPLIMIENTO DE NOMs: verificar que todo producto importado cuenta con la etiqueta en español y cumple NOM aplicable.
8. RESGUARDO DE CERTIFICADOS DE ORIGEN: al menos 5 años para demostrar que se aplicó T-MEC correctamente.""",
"LA Art. 36, CFF Art. 30","control interno importador expediente pedimento conciliación NOM fracciones TIGIE 5 años",2026),

("contabilidad","papeles_trabajo","Papeles de Trabajo Contable — Organización",
"""Organización recomendada de papeles de trabajo para una importadora (por mes):
CARPETA MENSUAL:
  1. Balanza de comprobación del mes
  2. Conciliación bancaria (una por cuenta bancaria)
  3. Cédula de IVA acreditable (listado de CFDIs de compra + pedimentos)
  4. Cédula de IVA trasladado (listado de CFDIs de venta emitidos)
  5. Cálculo de pago provisional ISR
  6. Nómina del mes + CFDI de nómina timbrados
  7. Declaraciones presentadas (captura de pantalla o acuse)
  8. Pedimentos del mes (copia del pedimento + factura del proveedor)
HERRAMIENTAS RECOMENDADAS:
  - Contpaq i / CONTPAQi: software contable local, integrado SAT
  - Aspel COI: alternativa
  - Excel: para cédulas de conciliación, cálculos ISR provisional
  - Portal SAT: para verificar CFDIs recibidos (descargar masivamente)""",
"CFF Art. 30, CINIF NIF A-4","papeles trabajo balanza conciliación bancaria cédula IVA ISR nómina pedimentos declaraciones",2026),

]

# ──────────────────────────────────────────────────────────────────────────────
# CARGA EN BASE DE DATOS
# ──────────────────────────────────────────────────────────────────────────────

def seed():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    # Limpiar y recargar
    cur.execute("DELETE FROM knowledge_base")

    rows = [(t, st, title, content, source, kw, yr) for t, st, title, content, source, kw, yr in KNOWLEDGE]

    execute_values(cur, """
        INSERT INTO knowledge_base (topic, subtopic, title, content, source, keywords, year)
        VALUES %s
    """, rows)

    conn.commit()
    count = cur.execute("SELECT COUNT(*) FROM knowledge_base")
    cur.execute("SELECT COUNT(*) FROM knowledge_base")
    count = cur.fetchone()[0]
    print(f"✅ {count} entradas cargadas en knowledge_base")

    # Resumen por topic
    cur.execute("SELECT topic, COUNT(*) FROM knowledge_base GROUP BY topic ORDER BY topic")
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]} entradas")

    cur.close()
    conn.close()


if __name__ == "__main__":
    seed()
