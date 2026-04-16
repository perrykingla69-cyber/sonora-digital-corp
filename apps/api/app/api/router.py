from fastapi import APIRouter

from . import alertas, auth, contactos, dashboard, empleados, facturas, leads, memory, ops, tenants
from .v1 import agents, signup, agent_deployments, bots

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

# V1 API with /api/v1 prefix
api_router.include_router(agents.router, prefix="/api/v1/agents", tags=["agents-hermes"])

# Fase 1 — SaaS Platform endpoints
api_router.include_router(signup.router, prefix="/api/v1/users", tags=["users"])
api_router.include_router(agent_deployments.router, prefix="/api/v1/agents", tags=["agent-deployments"])
api_router.include_router(bots.router, prefix="/api/v1/bots", tags=["bots"])
