"""SQLAlchemy models — todos los modelos de la plataforma MYSTIC."""

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
    nombre = Column(String, nullable=False)
    rfc = Column(String)
    nss = Column(String)
    puesto = Column(String)
    salario_mensual = Column(Float, default=0.0)
    tipo_contrato = Column(String, default="indefinido")
    activo = Column(Boolean, default=True)
    fecha_ingreso = Column(DateTime(timezone=True), default=_now)


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
    numero_pedimento = Column(String)
    aduana = Column(String)
    fecha_entrada = Column(DateTime(timezone=True), nullable=True)
    valor_comercial = Column(Float, default=0.0)
    moneda = Column(String, default="USD")
    tipo_cambio = Column(Float, default=1.0)
    valor_aduana_mxn = Column(Float, default=0.0)
    fraccion_arancelaria = Column(String)
    descripcion = Column(Text)
    igi_porcentaje = Column(Float, default=0.0)
    igi_monto = Column(Float, default=0.0)
    iva_importacion = Column(Float, default=0.0)
    dta = Column(Float, default=0.0)
    total_contribuciones = Column(Float, default=0.0)
    incoterm = Column(String)
    estado = Column(String, default="borrador")
    folio_vucem = Column(String, nullable=True)
    fecha_presentacion_vucem = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)


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
