"""SQLAlchemy models — todos los modelos de la plataforma HERMES."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from database import Base


def _now():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4())


class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True, default=_uuid)
    nombre = Column(String, nullable=False)
    rfc = Column(String, nullable=False)
    direccion = Column(Text)
    plan = Column(String, default="basico")  # basico, business, pro, magia
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_now)


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String, default="contador")  # ceo, contador, admin
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_now)


class Factura(Base):
    __tablename__ = "facturas"
    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    tipo = Column(String, default="ingreso")       # ingreso, egreso
    folio = Column(String)
    uuid_cfdi = Column(String)
    rfc_emisor = Column(String)
    rfc_receptor = Column(String)
    nombre_emisor = Column(String)
    nombre_receptor = Column(String)
    subtotal = Column(Float, default=0.0)
    iva = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    moneda = Column(String, default="MXN")
    tipo_cambio = Column(Float, default=1.0)
    estado = Column(String, default="pendiente")  # pendiente, pagada, cancelada
    tipo_pago = Column(String, default="pendiente")  # prepagado, pendiente, pagado, cancelado
    regimen_fiscal = Column(String, default="general")  # resico_pf, resico_pm, general, honorarios
    isr_retenido = Column(Float, default=0.0)   # ISR retenido 1.25% (RESICO Art. 113-J)
    iva_retenido = Column(Float, default=0.0)   # IVA retenido (si aplica)
    fecha_emision = Column(DateTime(timezone=True))
    fecha_pago = Column(DateTime(timezone=True), nullable=True)
    concepto = Column(Text)
    xml_cfdi = Column(Text, nullable=True)
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)


class Empleado(Base):
    __tablename__ = "empleados"
    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    # Datos personales
    nombre = Column(String, nullable=False)
    curp = Column(String)
    rfc = Column(String)
    nss = Column(String)                         # Número Seguro Social IMSS
    numero_empleado = Column(String)
    # Datos laborales
    puesto = Column(String)
    departamento = Column(String)
    tipo_contrato = Column(String, default="indefinido")  # indefinido|temporal|obra|honorarios
    regimen_imss = Column(String, default="sueldos_salarios")  # sueldos_salarios|honorarios|asimilados
    fecha_ingreso = Column(DateTime(timezone=True), default=_now)
    fecha_baja = Column(DateTime(timezone=True), nullable=True)
    activo = Column(Boolean, default=True)
    # Salarios
    tipo_salario = Column(String, default="mensual")  # mensual|quincenal|semanal|diario
    salario_mensual = Column(Float, default=0.0)
    salario_diario = Column(Float, default=0.0)       # salario_mensual / 30.4
    salario_integrado = Column(Float, default=0.0)    # salario_diario * factor_integracion
    factor_integracion = Column(Float, default=1.0452) # 1 + (vacac+prima+aguinaldo)/365
    # INFONAVIT
    tiene_infonavit = Column(Boolean, default=False)
    numero_credito_infonavit = Column(String)
    descuento_infonavit = Column(Float, default=0.0)
    tipo_descuento_infonavit = Column(String, default="vsm")  # vsm|porcentaje|fijo
    # IMSS — prima de riesgo de trabajo
    prima_riesgo_trabajo = Column(Float, default=0.005)  # 0.5% mínimo clase I
    # Datos bancarios
    banco = Column(String)
    clabe = Column(String)                        # 18 dígitos CLABE interbancaria
    # Prestaciones adicionales
    caja_ahorro_pct = Column(Float, default=0.0)
    prestamos = Column(Float, default=0.0)        # Descuento por préstamos activos
    vales_despensa = Column(Float, default=0.0)   # Exento hasta 40% UMA mensual
    notas = Column(Text)


class Nomina(Base):
    __tablename__ = "nominas"
    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    empleado_id = Column(String, ForeignKey("empleados.id"), nullable=False)
    periodo_inicio = Column(DateTime(timezone=True))
    periodo_fin = Column(DateTime(timezone=True))
    salario_bruto = Column(Float, default=0.0)
    isr_retenido = Column(Float, default=0.0)
    imss_retenido = Column(Float, default=0.0)
    subsidio_empleo = Column(Float, default=0.0)
    salario_neto = Column(Float, default=0.0)
    estado = Column(String, default="pendiente")
    created_at = Column(DateTime(timezone=True), default=_now)


class CierreMes(Base):
    __tablename__ = "cierres_mes"
    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    año = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    ingresos_total = Column(Float, default=0.0)
    egresos_total = Column(Float, default=0.0)
    iva_cobrado = Column(Float, default=0.0)
    iva_pagado = Column(Float, default=0.0)
    iva_neto = Column(Float, default=0.0)
    isr_estimado = Column(Float, default=0.0)
    utilidad_bruta = Column(Float, default=0.0)
    resumen_json = Column(JSONB, nullable=True)
    estado = Column(String, default="borrador")  # borrador, cerrado
    created_at = Column(DateTime(timezone=True), default=_now)


class TipoCambio(Base):
    __tablename__ = "tipos_cambio"
    id = Column(String, primary_key=True, default=_uuid)
    fecha = Column(DateTime(timezone=True), default=_now)
    usd_mxn = Column(Float, nullable=False)
    fuente = Column(String, default="DOF")
    created_at = Column(DateTime(timezone=True), default=_now)


class MVE(Base):
    __tablename__ = "mves"
    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=False)
    # Proveedor
    proveedor_nombre = Column(String, nullable=False)
    proveedor_pais = Column(String)
    proveedor_tax_id = Column(String)
    proveedor_direccion = Column(Text)
    # Factura comercial
    numero_factura = Column(String)
    fecha_factura = Column(DateTime(timezone=True), nullable=True)
    descripcion_mercancias = Column(Text)
    fraccion_arancelaria = Column(String)
    cantidad = Column(Float, default=1.0)
    unidad_medida = Column(String)
    # Valores
    incoterm = Column(String)
    valor_factura = Column(Float, default=0.0)
    moneda = Column(String, default="USD")
    tipo_cambio = Column(Float, default=1.0)
    valor_factura_mxn = Column(Float, default=0.0)
    flete = Column(Float, default=0.0)
    seguro = Column(Float, default=0.0)
    otros_cargos = Column(Float, default=0.0)
    descuentos = Column(Float, default=0.0)
    regalias = Column(Float, default=0.0)
    asistencias = Column(Float, default=0.0)
    valor_en_aduana = Column(Float, default=0.0)
    # Contribuciones
    tasa_igi = Column(Float, default=0.0)
    igi = Column(Float, default=0.0)
    iva_importacion = Column(Float, default=0.0)
    dta = Column(Float, default=0.0)
    # Método valoración (Art. 45-50 Ley Aduanera)
    metodo_valoracion = Column(Integer, default=1)
    justificacion_metodo = Column(Text)
    hay_vinculacion = Column(Boolean, default=False)
    justificacion_vinculacion = Column(Text)
    # Semáforo anti-multa
    semaforo = Column(String, nullable=True)       # red | yellow | green
    semaforo_errores = Column(JSONB, nullable=True)
    semaforo_validado_at = Column(DateTime(timezone=True), nullable=True)
    # Estado y VUCEM
    estado = Column(String, default="borrador")    # borrador | lista | presentada | pagada
    folio_vucem = Column(String, nullable=True)
    pedimento_numero = Column(String, nullable=True)
    notas = Column(Text)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class Contacto(Base):
    """Directorio: clientes, proveedores, agentes aduanales, importadores."""
    __tablename__ = "contactos"
    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    # Tipo y categorías
    tipo = Column(String, nullable=False)  # cliente|proveedor|agente_aduanal|importador|ambos
    categorias = Column(JSONB, default=list)  # ["cliente","proveedor"]
    # Datos fiscales
    razon_social = Column(String, nullable=False)
    rfc = Column(String)
    curp = Column(String)
    regimen_fiscal = Column(String)        # 601, 612, 626, etc.
    uso_cfdi = Column(String, default="G03")
    pais = Column(String, default="México")
    # Datos de contacto
    contacto_nombre = Column(String)
    email = Column(String)
    email2 = Column(String)
    telefono = Column(String)
    celular = Column(String)
    whatsapp = Column(String)
    # Dirección
    direccion_fiscal = Column(Text)
    ciudad = Column(String)
    estado_mx = Column(String)
    cp = Column(String)
    # Comercial
    condicion_pago = Column(Integer, default=30)  # días de crédito
    limite_credito = Column(Float, default=0.0)
    moneda = Column(String, default="MXN")
    # Bancario
    banco = Column(String)
    cuenta = Column(String)
    clabe = Column(String)
    # Agente aduanal (solo si tipo=agente_aduanal)
    patente_aduanal = Column(String)          # 5 dígitos
    aduana_habitual = Column(String)          # Nogales, Tijuana, etc.
    # Proveedor USA / extranjero
    tax_id = Column(String)                   # EIN/SSN para USA
    direccion_extranjero = Column(Text)
    # Métricas (auto-calculadas)
    total_facturas = Column(Integer, default=0)
    monto_total_compras = Column(Float, default=0.0)
    monto_total_ventas = Column(Float, default=0.0)
    ultima_operacion = Column(DateTime(timezone=True), nullable=True)
    # Estado
    activo = Column(Boolean, default=True)
    notas = Column(Text)
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class Lead(Base):
    __tablename__ = "leads"
    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    nombre = Column(String, nullable=False)
    empresa = Column(String)
    email = Column(String)
    telefono = Column(String)
    status = Column(String, default="nuevo")  # nuevo, contactado, calificado, propuesta, ganado, perdido
    notas = Column(Text)
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class AlertaConfig(Base):
    __tablename__ = "alertas_config"
    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    hora_manana = Column(String, default="06:00")
    hora_tarde = Column(String, default="18:00")
    activo = Column(Boolean, default=True)
    chat_id_telegram = Column(String)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class GSDTask(Base):
    __tablename__ = "gsd_tasks"
    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    usuario_id = Column(String, ForeignKey("usuarios.id"), nullable=False)
    titulo = Column(String, nullable=False)
    descripcion = Column(Text)
    prioridad = Column(Integer, default=1)  # 1=MIT, 2=normal, 3=baja
    completada = Column(Boolean, default=False)
    fecha_limite = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(String, primary_key=True, default=_uuid)
    tenant_id = Column(String, nullable=True)
    usuario_id = Column(String, nullable=True)
    accion = Column(String)
    recurso = Column(String)
    detalle = Column(JSONB, nullable=True)
    ip = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)


# ── BRAIN SWARM — Memoria y Aprendizaje ──────────────────────────────────────

class BrainSession(Base):
    """Memoria conversacional cross-session por canal (WhatsApp, Telegram, Dashboard)."""
    __tablename__ = "brain_sessions"
    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, unique=True, nullable=False, index=True)
    # session_id = "{channel}:{channel_id}"  ej: "whatsapp:5216622681111"
    tenant_id = Column(String, nullable=True)
    channel = Column(String, default="api")   # whatsapp | telegram | dashboard | api
    messages = Column(JSONB, default=list)    # [{role, content, ts}] últimas 10
    last_activity = Column(DateTime(timezone=True), default=_now, onupdate=_now)
    created_at = Column(DateTime(timezone=True), default=_now)


class BrainFeedback(Base):
    """Auto-aprendizaje: Q&A que el usuario calificó como buenas/malas."""
    __tablename__ = "brain_feedback"
    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, nullable=True)
    tenant_id = Column(String, nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    rating = Column(Integer, default=0)       # +1 buena | -1 mala
    context = Column(String, default="fiscal")
    indexed_qdrant = Column(Boolean, default=False)  # re-indexado como conocimiento
    created_at = Column(DateTime(timezone=True), default=_now)


class AccessLog(Base):
    """Registro de accesos: quién entró, desde qué IP, en qué canal."""
    __tablename__ = "access_logs"
    id = Column(String, primary_key=True, default=_uuid)
    usuario_id = Column(String, nullable=True)
    email = Column(String, nullable=True)
    tenant_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    accion = Column(String)   # login_ok | login_fail | logout
    canal = Column(String, default="web")
    detalle = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)


class PasswordResetToken(Base):
    """Tokens de recuperación de contraseña (válidos 1h, uso único)."""
    __tablename__ = "password_reset_tokens"
    id = Column(String, primary_key=True, default=_uuid)
    usuario_id = Column(String, ForeignKey("usuarios.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=_now)
