#!/usr/bin/env python3
"""
seed_roles_qdrant.py — Alimenta Qdrant con conocimiento para roles clave:
contador_mx, admin_mx, CEO, CTO, auditor.
Usa Ollama nomic-embed-text (local, sin costo).
"""
import json, uuid, urllib.request, urllib.error, sys, time

QDRANT   = "http://localhost:6333"
OLLAMA   = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"

# ── Conocimiento por colección ─────────────────────────────────────────────────
KNOWLEDGE = {
    "contador_mx": [
        ("Declaración mensual RESICO", "RESICO (Régimen Simplificado de Confianza) aplica a personas físicas con ingresos hasta $3.5M anuales. Pagos mensuales definitivos del ISR: 1% a 2.5% sobre ingresos cobrados. Sin deducción de gastos. Declaración vía app SAT o portal. Fecha límite: día 17 del mes siguiente."),
        ("DIOT mensual obligaciones", "La DIOT (Declaración Informativa de Operaciones con Terceros) se presenta mensualmente antes del día 17. Reporta proveedores con IVA acreditable. Se captura en portal SAT o DEM. Omitir genera multa de $1,590 a $15,900 MXN por declaración."),
        ("Cierre contable mensual", "El cierre mensual incluye: conciliación bancaria, revisión de cuentas por cobrar/pagar, cálculo de depreciaciones, provisión de nómina, determinación de ISR e IVA a pagar. Se recomienda cerrar dentro de los primeros 5 días hábiles del mes siguiente."),
        ("Facturación CFDI 4.0 errores comunes", "Errores frecuentes CFDI 4.0: RFC receptor incorrecto, uso CFDI no válido para el giro, régimen fiscal del emisor incorrecto, domicilio fiscal sin código postal, complemento de pago omitido en pagos diferidos. El SAT puede rechazar el timbre en segundos."),
        ("ISR personas morales", "Personas morales pagan ISR a tasa del 30% sobre utilidad fiscal. Pagos provisionales mensuales basados en coeficiente de utilidad. Declaración anual en marzo. Deducciones permitidas: gastos estrictamente indispensables para la actividad, documentados con CFDI."),
        ("IVA mensual cálculo", "IVA a cargo = IVA trasladado (cobrado a clientes) - IVA acreditable (pagado a proveedores). Tasa general 16%, frontera norte 8%. Si acreditable > trasladado: saldo a favor que puede compensarse o solicitarse en devolución. Declaración día 17 de cada mes."),
        ("Nómina y IMSS obligaciones patrón", "El patrón paga cuotas IMSS: enfermedad/maternidad, riesgos trabajo, invalidez/vida, guarderías, retiro/cesantía/vejez. Suma aproximada: 25-30% adicional sobre salario bruto. Pago bimestral cuotas obrero-patronales. Alta del trabajador antes del primer día laboral."),
        ("Conciliación bancaria", "La conciliación bancaria compara saldo en libros vs saldo bancario. Diferencias comunes: cheques en tránsito, depósitos en tránsito, cargos bancarios no registrados, errores contables. Debe realizarse mensualmente para detectar fraudes y errores oportunamente."),
        ("Régimen fiscal correcto para empresa", "Personas morales: Régimen General (30% ISR). Personas físicas: RESICO (hasta $3.5M), Actividad Empresarial (tarifa art. 152 LISR), Sueldos y Salarios, Arrendamiento, Honorarios, Dividendos. Elegir mal el régimen genera créditos fiscales y multas."),
        ("Carta porte CFDI obligatorio transporte", "El Complemento Carta Porte es obligatorio para traslado de mercancías por carretera, ferroviario, marítimo y aéreo. Desde 2022. Requiere datos del transportista, vehículo, mercancía, origen y destino. Sin él, la mercancía puede ser detenida por la autoridad."),
        ("Declaración anual personas físicas", "Personas físicas presentan declaración anual en abril. Incluye todos los ingresos del año: sueldos, honorarios, arrendamiento, enajenación de bienes. Deducciones personales: gastos médicos, colegiaturas, donativos, intereses hipotecarios. Límite deducciones: 15% del ingreso o 5 UMAs anuales."),
        ("Buzón tributario obligaciones", "El Buzón Tributario es el canal oficial del SAT para notificaciones. Obligatorio habilitarlo. Si no está habilitado, las notificaciones se dan por estrados (tablero SAT) y el contribuyente pierde plazos para defenderse. Revisar semanalmente para evitar sorpresas."),
    ],
    "admin_mx": [
        ("Control de gastos empresa PYME", "Sistema de control de gastos para PYMEs: 1) Política de gastos por escrito con límites por área, 2) Aprobaciones según monto (gerente/dirección), 3) CFDI obligatorio para todo gasto deducible, 4) Conciliación semanal de tarjetas corporativas, 5) Reporte mensual de variación vs presupuesto."),
        ("Contratos laborales México", "Contrato individual de trabajo debe incluir: nombre/domicilio de partes, fecha inicio, tipo de jornada (diurna/nocturna/mixta), salario y forma de pago, días de descanso y vacaciones, lugar de trabajo. Contrato indeterminado es la regla. Contrato determinado requiere justificación."),
        ("IMSS alta trabajadores", "Alta IMSS antes del primer día de trabajo. Plataforma IMSS Digital o IDSE. Datos necesarios: CURP, NSS (si tiene), salario diario integrado, tipo de trabajador. Omisión: multa + liquidación retroactiva de cuotas + recargos. El trabajador tiene derecho a prestaciones desde el primer día."),
        ("Nómina cálculo completo", "Componentes nómina: salario base, partes proporcionales de aguinaldo (15 días/año), vacaciones, prima vacacional (25% mínimo), PTU (10% de utilidad fiscal). Retenciones: ISR según tabla, IMSS cuota obrera. Liquidación: 3 meses de salario + 20 días por año + partes proporcionales."),
        ("Administración de proveedores", "Gestión de proveedores: 1) Alta con CFDI de alta constitutiva o constancia SAT, 2) Validar RFC en lista negra SAT (Art. 69-B), 3) Contrato de servicios firmado, 4) Términos de pago claros (30/60/90 días), 5) Evaluación trimestral de calidad/precio, 6) Al menos 2 proveedores alternativos por categoría crítica."),
        ("Control de inventarios México", "Métodos valuación inventarios permitidos fiscalmente: PEPS (Primeras Entradas Primeras Salidas), Costo identificado, Costo promedio. El método debe mantenerse por al menos 5 años. Diferencias de inventario deben justificarse; las pérdidas sin justificación son ingreso acumulable."),
        ("Obligaciones laborales anuales", "Obligaciones anuales del patrón: reparto de PTU (antes del 30 mayo personas morales, 29 junio físicas), entrega de constancia de percepciones y retenciones (antes del 15 febrero), prima de antigüedad (12 días de salario/año a partir de 15 años de servicio), actualización de tabla de vacaciones."),
        ("Onboarding empleado nuevo", "Proceso onboarding: 1) Contrato firmado antes del primer día, 2) Alta IMSS, 3) Alta en nómina, 4) Apertura cuenta bancaria para dispersión, 5) Registro en sistema de asistencia, 6) Entrega de equipo con acta de recibo, 7) Capacitación obligatoria (Art. 153-A LFT), 8) Registro en STPS plataforma capacitación."),
    ],
    "fiscal_mx": [
        ("Artículo 69-B CFF proveedores fantasma", "El Art. 69-B CFF permite al SAT presumir operaciones inexistentes cuando el emisor no tiene activos, personal o instalaciones para prestar el servicio. Si tu proveedor está en lista negra SAT, pierdes la deducción y el acreditamiento de IVA. Verificar RFC del proveedor en: sat.gob.mx/69B antes de pagar."),
        ("Deducción de gastos requisitos", "Para deducir un gasto: 1) CFDI válido con timbre SAT, 2) Estrictamente indispensable para la actividad, 3) Efectivamente pagado (para flujo de efectivo) o devengado (acumulación), 4) No en lista de no deducibles (Art. 28 LISR), 5) Retención ISR si aplica (honorarios, arrendamiento)."),
        ("Impuesto sobre nómina estatal", "El Impuesto sobre Nómina (ISN) es estatal. Varía por estado: Sonora 2%, CDMX 3%, Nuevo León 3%, Jalisco 2.5%. Se paga mensualmente a la Secretaría de Finanzas estatal. Base: total de remuneraciones pagadas a trabajadores. No es deducible de ISR federal pero sí es gasto de operación."),
        ("Factura global público en general", "La factura global se emite por operaciones con público en general (sin RFC específico). Puede ser diaria, semanal, mensual o bimestral (RESICO). RFC genérico: XAXX010101000 para nacionales, XEXX010101000 para extranjeros. Incluye todos los comprobantes de venta del período."),
        ("Compensación de saldos a favor", "Desde 2019, la compensación universal está restringida. Solo puedes compensar saldos a favor de IVA contra IVA a cargo del mismo período. ISR a favor solo puede compensarse contra ISR. Para compensar entre impuestos diferentes, tramitar devolución. Formulario 32 en portal SAT."),
    ],
    "ceo_mx": [
        ("KPIs financieros para CEO PYME", "KPIs clave para CEO de PYME mexicana: 1) Margen bruto (>40% para servicios), 2) EBITDA margin (>15%), 3) Días de cuentas por cobrar (<30 días ideal), 4) Rotación de inventario (según sector), 5) Punto de equilibrio mensual, 6) Flujo de caja operativo positivo, 7) Costo de adquisición de cliente vs LTV."),
        ("Planeación fiscal estratégica CEO", "El CEO debe revisar trimestralmente: ISR anual estimado vs pagos provisionales, posibilidad de diferir ingresos al siguiente ejercicio, deducibilidad de inversiones (maquinaria 25%, equipo transporte 25%, edificios 5%), beneficios fiscales por zona geográfica (frontera norte), crédito al IEPS."),
        ("Expansión empresa México decisiones", "Para expandir empresa en México: 1) Nueva sucursal (RFC único, alta ante SAT del establecimiento), 2) Nueva razón social (costos operativos, pero aislamiento de riesgo), 3) Franquicia (requiere contrato de franquicia registrado y carta de revelación), 4) Joint Venture (acuerdo de colaboración o nueva sociedad)."),
        ("Financiamiento PYME México opciones", "Opciones de financiamiento para PYMEs: 1) Crédito bancario PyME (BBVA, Banorte, HSBC) — requiere 2 años de operación y estados financieros, 2) NAFIN garantías (avala hasta 70% del crédito), 3) Factoraje financiero — adelanto de cuentas por cobrar, 4) Crowdfunding plataformas CNBV, 5) Capital privado/ángeles inversores."),
        ("Gobierno corporativo PYME", "Buenas prácticas de gobierno corporativo para PYME: 1) Consejo de administración o directivos con funciones definidas, 2) Separar cuentas personales de empresa (nunca mezclar), 3) Acta de asamblea para decisiones importantes, 4) Contrato entre socios con pacto de accionistas, 5) Seguros de responsabilidad civil y daños."),
        ("Valuación empresa para vender o invertir", "Métodos de valuación de empresa: 1) EBITDA x múltiplo (PYMEs mexicanas: 3x-6x EBITDA), 2) Flujo de caja descontado (DCF) — más preciso, requiere proyecciones 5 años, 3) Valor en libros (contable) — no refleja valor real de marca/cartera, 4) Transacciones comparables del sector. Contratar valuador externo para operaciones >$5M."),
        ("Distribución de utilidades México", "Distribución de dividendos en México: personas morales pagan ISR del 30% sobre utilidad fiscal. Al distribuir dividendos a socios personas físicas: retención adicional del 10% sobre el dividendo. Si el dividendo proviene de CUFIN (Cuenta de Utilidad Fiscal Neta), no paga impuesto adicional. Documentar en acta de asamblea."),
    ],
    "auditor_mx": [
        ("Auditoría interna PYME", "Proceso de auditoría interna para PYMEs: 1) Mapeo de riesgos operativos y financieros, 2) Revisión de controles internos (segregación de funciones), 3) Muestreo de transacciones (COSO framework), 4) Verificación de cumplimiento fiscal (SAT, IMSS, INFONAVIT), 5) Informe a dirección con hallazgos y plan de acción."),
        ("Riesgos fiscales empresa auditada", "Riesgos fiscales más comunes en auditoría: 1) Proveedores en lista 69-B sin aclaración, 2) Gastos no deducibles registrados como deducibles, 3) Retenciones de ISR no enteradas, 4) Diferencias entre declaraciones y contabilidad electrónica, 5) DIOT vs registros contables inconsistentes, 6) Nómina sin soporte documental completo."),
        ("Contabilidad electrónica SAT obligaciones", "Contabilidad electrónica obligatoria desde 2015: 1) Catálogo de cuentas con código agrupador SAT, 2) Balanza de comprobación mensual (XML), 3) Pólizas contables con UUID del CFDI relacionado, 4) Entrega bajo requerimiento o auditoría, no mensualmente. Software: CONTPAQi, Aspel COI, SAP. XML validado en portal SAT."),
        ("Control interno compras y pagos", "Control interno en proceso de compras: 1) Solicitud de compra autorizada, 2) Cotización mínimo 3 proveedores para montos >$50K, 3) Orden de compra numerada y autorizada, 4) Recepción con acta de conformidad, 5) Factura vs orden de compra (3 vías), 6) Pago solo con CFDI válido y validado en SAT, 7) Firma mancomunada para montos significativos."),
        ("Dictamen fiscal opcional IMCP", "El dictamen fiscal (antes obligatorio, ahora opcional) lo emite un Contador Público Certificado (CPC) afiliado al IMCP. Ventajas de presentarlo: el SAT no puede revisar los períodos dictaminados excepto por simulación. Para empresas >$100M ingresos o con ciertas características puede ser conveniente para reducir riesgo de revisión."),
        ("Fraude interno señales de alerta", "Señales de alerta de fraude interno: 1) Empleado que nunca toma vacaciones (control sobre proceso), 2) Proveedor con mismo domicilio/cuenta que empleado, 3) Gastos sin soporte o soportes alterados, 4) Diferencias recurrentes en inventarios, 5) Pagos a proveedores fuera de política, 6) Accesos múltiples al sistema desde diferentes IPs, 7) Cambios en datos bancarios de proveedores."),
        ("Revisión de estados financieros básica", "Análisis básico de estados financieros: 1) Razón de liquidez (activo circulante/pasivo circulante >1.5), 2) Razón de endeudamiento (pasivo total/activo total <0.6), 3) Rentabilidad sobre ventas (utilidad neta/ventas >5% PYME), 4) Rotación de cuentas por cobrar (ventas/CxC <12 veces/año), 5) Capital de trabajo positivo."),
    ],
}

def embed(text: str) -> list[float]:
    payload = json.dumps({"model": EMBED_MODEL, "prompt": text}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/embeddings", data=payload,
                                  headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["embedding"]

def ensure_collection(name: str, size: int = 768):
    try:
        urllib.request.urlopen(f"{QDRANT}/collections/{name}", timeout=5)
        print(f"  colección {name} existe")
    except urllib.error.HTTPError:
        payload = json.dumps({"vectors": {"size": size, "distance": "Cosine"}}).encode()
        req = urllib.request.Request(f"{QDRANT}/collections/{name}", data=payload,
                                      headers={"Content-Type": "application/json"}, method="PUT")
        urllib.request.urlopen(req, timeout=10)
        print(f"  colección {name} creada")

def upsert_points(collection: str, points: list[dict]):
    payload = json.dumps({"points": points}).encode()
    req = urllib.request.Request(f"{QDRANT}/collections/{collection}/points?wait=true",
                                  data=payload, headers={"Content-Type": "application/json"}, method="PUT")
    urllib.request.urlopen(req, timeout=30)

def seed_collection(name: str, docs: list[tuple]):
    print(f"\n→ Seeding {name} ({len(docs)} docs)...")
    ensure_collection(name)
    points = []
    for i, (titulo, contenido) in enumerate(docs):
        try:
            vector = embed(f"{titulo}. {contenido}")
            points.append({
                "id": str(uuid.uuid4()),
                "vector": vector,
                "payload": {"titulo": titulo, "contenido": contenido,
                            "coleccion": name, "fuente": "HERMES Knowledge Base 2026"},
            })
            print(f"  [{i+1}/{len(docs)}] {titulo[:50]}")
        except Exception as e:
            print(f"  ERROR en '{titulo}': {e}", file=sys.stderr)
        time.sleep(0.3)
    if points:
        upsert_points(name, points)
        print(f"  ✅ {len(points)} vectores insertados en {name}")

if __name__ == "__main__":
    print("=== HERMES Qdrant Seed — Roles clave ===")
    for collection, docs in KNOWLEDGE.items():
        seed_collection(collection, docs)
    print("\n✅ Seed completo.")
