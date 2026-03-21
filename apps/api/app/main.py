from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth, facturas, ops, tenants
from .core.settings import get_settings

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ops.router)
app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(facturas.router)
