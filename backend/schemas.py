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
    rfc: Optional[str] = None
    nss: Optional[str] = None
    puesto: Optional[str] = None
    salario_mensual: float = 0.0
    tipo_contrato: str = "indefinido"


class EmpleadoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    nombre: str
    rfc: Optional[str] = None
    nss: Optional[str] = None
    puesto: Optional[str] = None
    salario_mensual: float
    tipo_contrato: str
    activo: bool
    fecha_ingreso: Optional[datetime] = None


# ── NOMINA ──

class NominaCreate(BaseModel):
    empleado_id: str
    periodo_inicio: datetime
    periodo_fin: datetime
    salario_bruto: float = 0.0


class NominaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    empleado_id: str
    periodo_inicio: Optional[datetime] = None
    periodo_fin: Optional[datetime] = None
    salario_bruto: float
    isr_retenido: float
    imss_retenido: float
    subsidio_empleo: float
    salario_neto: float
    estado: str
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
