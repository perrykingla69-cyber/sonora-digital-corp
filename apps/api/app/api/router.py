from fastapi import APIRouter

from . import alertas, auth, contactos, dashboard, empleados, facturas, leads, memory, ops, tenants
from .v1 import agents, signup, agent_deployments, bots, gamification, fiscal, academy

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
api_router.include_router(fiscal.router, prefix="/api/v1/agents", tags=["fiscal-agent"])

# Fase 1 — SaaS Platform endpoints
api_router.include_router(signup.router, prefix="/api/v1/users", tags=["users"])
api_router.include_router(agent_deployments.router, prefix="/api/v1/agents", tags=["agent-deployments"])
api_router.include_router(bots.router, prefix="/api/v1/bots", tags=["bots"])

# Gamification
api_router.include_router(gamification.router, prefix="/api/v1", tags=["gamification"])

# ABE Music Academy — /api/academy/* (frontend BASE = sonoradigitalcorp.com/api)
api_router.include_router(academy.router, prefix="/api", tags=["ABE Academy"])
