"""
Agent Factory — Crea contenedores Docker para agentes IA.
Servicio independiente que recibe requests de hermes-api.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from factory import router as factory_router

app = FastAPI(
    title="Agent Factory",
    description="Crea y gestiona contenedores Docker para agentes IA",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(factory_router, prefix="/factory", tags=["factory"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "agent-factory"}
