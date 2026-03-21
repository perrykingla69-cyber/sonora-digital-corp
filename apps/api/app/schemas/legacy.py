"""Re-export legacy Pydantic schemas while the v2 schema layer is normalized."""
from ..core import legacy  # noqa: F401
from schemas import (  # type: ignore
    ContactoCreate,
    ContactoResponse,
    DashboardResponse,
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
    "ContactoCreate",
    "ContactoResponse",
    "DashboardResponse",
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
