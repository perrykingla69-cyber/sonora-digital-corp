from .alertas import AlertaConfigUpdate
from .dashboard import DashboardResponse
from .leads import LeadCreate, LeadUpdate
from .legacy import (
    ContactoCreate,
    ContactoResponse,
    EmpleadoCreate,
    EmpleadoResponse,
    FacturaCreate,
    FacturaResponse,
    LoginRequest,
    LoginResponse,
    TenantCreate,
    TenantResponse,
    UsuarioCreate,
    UsuarioResponse,
)

__all__ = [
    "AlertaConfigUpdate",
    "DashboardResponse",
    "LeadCreate",
    "LeadUpdate",
    "ContactoCreate",
    "ContactoResponse",
    "EmpleadoCreate",
    "EmpleadoResponse",
    "FacturaCreate",
    "FacturaResponse",
    "LoginRequest",
    "LoginResponse",
    "TenantCreate",
    "TenantResponse",
    "UsuarioCreate",
    "UsuarioResponse",
]
