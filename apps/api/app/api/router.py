from fastapi import APIRouter

from . import alertas, auth, contactos, dashboard, empleados, facturas, leads, memory, ops, tenants

api_router = APIRouter()
api_router.include_router(ops.router)
api_router.include_router(auth.router)
api_router.include_router(tenants.router)
api_router.include_router(facturas.router)
api_router.include_router(empleados.router)
api_router.include_router(contactos.router)
api_router.include_router(dashboard.router)
api_router.include_router(leads.router)
api_router.include_router(alertas.router)

api_router.include_router(memory.router)
