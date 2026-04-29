"""Compatibility shim — legacy schemas while v2 normalization is in progress."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DashboardResponse(BaseModel):
    tenant_id: str
    total_contacts: int = 0
    total_invoices: int = 0
    total_employees: int = 0
    mrr: float = 0.0
    generated_at: datetime = datetime.utcnow()


class ContactoCreate(BaseModel):
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None


class ContactoResponse(ContactoCreate):
    id: str
    created_at: datetime


class EmpleadoCreate(BaseModel):
    nombre: str
    puesto: Optional[str] = None
    salario: Optional[float] = None


class EmpleadoResponse(EmpleadoCreate):
    id: str
    created_at: datetime


class FacturaCreate(BaseModel):
    folio: str
    monto: float
    concepto: Optional[str] = None


class FacturaResponse(FacturaCreate):
    id: str
    created_at: datetime


class LoginRequest(BaseModel):
    email: str
    password: str
    tenant_slug: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: str
    user_id: str


class TenantCreate(BaseModel):
    slug: str
    name: str
    plan: str = "starter"


class TenantResponse(TenantCreate):
    id: str
    created_at: datetime


class UsuarioCreate(BaseModel):
    email: str
    password: str
    full_name: str


class UsuarioResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str


__all__ = [
    "DashboardResponse", "ContactoCreate", "ContactoResponse",
    "EmpleadoCreate", "EmpleadoResponse", "FacturaCreate", "FacturaResponse",
    "LoginRequest", "LoginResponse", "TenantCreate", "TenantResponse",
    "UsuarioCreate", "UsuarioResponse",
]
