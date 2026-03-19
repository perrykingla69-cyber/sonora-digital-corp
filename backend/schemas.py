"""Pydantic schemas para validación de requests y responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


# ── AUTH ──

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: "UsuarioResponse"


# ── USUARIOS ──

class UsuarioCreate(BaseModel):
    tenant_id: str
    email: str
    password: str
    nombre: str
    rol: str = "contador"
    telegram_id: Optional[str] = None


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    email: str
    nombre: str
    rol: str
    activo: bool
    created_at: Optional[datetime] = None


# ── TENANTS ──

class TenantCreate(BaseModel):
    nombre: str
    rfc: str
    direccion: Optional[str] = None
    plan: str = "basico"


class TenantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nombre: str
    rfc: str
    direccion: Optional[str] = None
    plan: str
    activo: bool
    created_at: Optional[datetime] = None


# ── FACTURAS ──

class FacturaCreate(BaseModel):
    tipo: str = "ingreso"
    folio: Optional[str] = None
    uuid_cfdi: Optional[str] = None
    rfc_emisor: Optional[str] = None
    rfc_receptor: Optional[str] = None
    nombre_emisor: Optional[str] = None
    nombre_receptor: Optional[str] = None
    subtotal: float = 0.0
    iva: float = 0.0
    total: float = 0.0
    moneda: str = "MXN"
    tipo_cambio: float = 1.0
    estado: str = "pendiente"
    fecha_emision: Optional[datetime] = None
    concepto: Optional[str] = None
    producto_tipo: Optional[str] = None
    folio_sat: Optional[str] = None


class FacturaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    tipo: str
    folio: Optional[str] = None
    uuid_cfdi: Optional[str] = None
    rfc_emisor: Optional[str] = None
    rfc_receptor: Optional[str] = None
    nombre_emisor: Optional[str] = None
    nombre_receptor: Optional[str] = None
    subtotal: float
    iva: float
    total: float
    moneda: str
    tipo_cambio: float
    estado: str
    fecha_emision: Optional[datetime] = None
    concepto: Optional[str] = None
    created_at: Optional[datetime] = None


# ── EMPLEADOS ──

class EmpleadoCreate(BaseModel):
    nombre: str
    curp: Optional[str] = None
    rfc: Optional[str] = None
    nss: Optional[str] = None
    numero_empleado: Optional[str] = None
    puesto: Optional[str] = None
    departamento: Optional[str] = None
    tipo_contrato: str = "indefinido"
    regimen_imss: str = "sueldos_salarios"
    fecha_ingreso: Optional[datetime] = None
    tipo_salario: str = "mensual"
    salario_mensual: float = 0.0
    factor_integracion: float = 1.0452
    prima_riesgo_trabajo: float = 0.005
    tiene_infonavit: bool = False
    numero_credito_infonavit: Optional[str] = None
    descuento_infonavit: float = 0.0
    tipo_descuento_infonavit: str = "vsm"
    banco: Optional[str] = None
    clabe: Optional[str] = None
    caja_ahorro_pct: float = 0.0
    prestamos: float = 0.0
    vales_despensa: float = 0.0
    notas: Optional[str] = None


class EmpleadoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    nombre: str
    curp: Optional[str] = None
    rfc: Optional[str] = None
    nss: Optional[str] = None
    numero_empleado: Optional[str] = None
    puesto: Optional[str] = None
    departamento: Optional[str] = None
    tipo_contrato: str = "indefinido"
    regimen_imss: Optional[str] = None
    fecha_ingreso: Optional[datetime] = None
    fecha_baja: Optional[datetime] = None
    tipo_salario: Optional[str] = None
    salario_mensual: float = 0.0
    salario_diario: float = 0.0
    salario_integrado: float = 0.0
    factor_integracion: float = 1.0452
    prima_riesgo_trabajo: float = 0.005
    tiene_infonavit: bool = False
    numero_credito_infonavit: Optional[str] = None
    descuento_infonavit: float = 0.0
    tipo_descuento_infonavit: Optional[str] = None
    banco: Optional[str] = None
    clabe: Optional[str] = None
    caja_ahorro_pct: float = 0.0
    prestamos: float = 0.0
    vales_despensa: float = 0.0
    notas: Optional[str] = None
    activo: bool = True


# ── NOMINA ──

class NominaCreate(BaseModel):
    empleado_id: str
    periodo_inicio: datetime
    periodo_fin: datetime
    percepciones_extra: float = 0.0


class NominaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    empleado_id: str
    periodo_inicio: Optional[datetime] = None
    periodo_fin: Optional[datetime] = None
    salario_bruto: float = 0.0
    isr_retenido: float = 0.0
    imss_retenido: float = 0.0
    subsidio_empleo: float = 0.0
    salario_neto: float = 0.0
    estado: str = "pendiente"
    created_at: Optional[datetime] = None


# ── CONTACTOS (Clientes/Proveedores/Agentes) ──

class ContactoCreate(BaseModel):
    tipo: str  # cliente|proveedor|agente_aduanal|importador|ambos
    razon_social: str
    rfc: Optional[str] = None
    curp: Optional[str] = None
    regimen_fiscal: Optional[str] = None
    uso_cfdi: str = "G03"
    pais: str = "México"
    contacto_nombre: Optional[str] = None
    email: Optional[str] = None
    email2: Optional[str] = None
    telefono: Optional[str] = None
    celular: Optional[str] = None
    whatsapp: Optional[str] = None
    direccion_fiscal: Optional[str] = None
    ciudad: Optional[str] = None
    estado_mx: Optional[str] = None
    cp: Optional[str] = None
    condicion_pago: int = 30
    limite_credito: float = 0.0
    moneda: str = "MXN"
    banco: Optional[str] = None
    cuenta: Optional[str] = None
    clabe: Optional[str] = None
    patente_aduanal: Optional[str] = None
    aduana_habitual: Optional[str] = None
    tax_id: Optional[str] = None
    direccion_extranjero: Optional[str] = None
    notas: Optional[str] = None


class ContactoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    tipo: str
    razon_social: str
    rfc: Optional[str] = None
    curp: Optional[str] = None
    regimen_fiscal: Optional[str] = None
    uso_cfdi: Optional[str] = None
    pais: Optional[str] = None
    contacto_nombre: Optional[str] = None
    email: Optional[str] = None
    email2: Optional[str] = None
    telefono: Optional[str] = None
    celular: Optional[str] = None
    whatsapp: Optional[str] = None
    direccion_fiscal: Optional[str] = None
    ciudad: Optional[str] = None
    estado_mx: Optional[str] = None
    cp: Optional[str] = None
    condicion_pago: int = 30
    limite_credito: float = 0.0
    moneda: Optional[str] = None
    banco: Optional[str] = None
    cuenta: Optional[str] = None
    clabe: Optional[str] = None
    patente_aduanal: Optional[str] = None
    aduana_habitual: Optional[str] = None
    tax_id: Optional[str] = None
    direccion_extranjero: Optional[str] = None
    total_facturas: int = 0
    monto_total_compras: float = 0.0
    monto_total_ventas: float = 0.0
    ultima_operacion: Optional[datetime] = None
    activo: bool = True
    notas: Optional[str] = None
    created_at: Optional[datetime] = None


# ── CIERRE ──

class CierreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    año: Optional[int] = None
    mes: Optional[int] = None
    ingresos_total: float = 0.0
    egresos_total: float = 0.0
    iva_cobrado: float = 0.0
    iva_pagado: float = 0.0
    iva_neto: float = 0.0
    isr_estimado: float = 0.0
    utilidad_bruta: float = 0.0
    estado: str = "borrador"
    created_at: Optional[datetime] = None


# ── DASHBOARD ──

class DashboardResponse(BaseModel):
    tenant_id: str
    periodo: str
    resumen: Dict[str, Any]
    alertas: List[str] = []
    kpis: Dict[str, Any] = {}
