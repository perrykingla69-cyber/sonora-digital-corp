"""
HERMES OS — FastAPI Backend
Orquestador: HERMES | Estratega: MYSTIC
Multi-tenant con RLS máxima seguridad
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time

from app.core.config import settings
from app.core.database import engine, init_db
from app.core.redis import redis_client
from app.api.v1 import auth, tenants, users, conversations, documents, webhooks, agents, content, payments
from app.webhooks import heygen as heygen_wh, fal as fal_wh


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await redis_client.close()


app = FastAPI(
    title="HERMES OS API",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)

# ── Seguridad: solo dominios autorizados ─────────────────────
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Tenant-ID"],
    max_age=600,
)


# ── Rate limiting básico por IP ───────────────────────────────
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host
    key = f"rl:{ip}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 60)
    if count > settings.RATE_LIMIT_PER_MINUTE:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests"},
        )
    response = await call_next(request)
    return response


# ── Timing header (solo dev) ─────────────────────────────────
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{(time.perf_counter() - start):.4f}"
    return response


# ── Routers ──────────────────────────────────────────────────
PREFIX = "/api/v1"
app.include_router(auth.router,          prefix=f"{PREFIX}/auth",          tags=["Auth"])
app.include_router(tenants.router,       prefix=f"{PREFIX}/tenants",       tags=["Tenants"])
app.include_router(users.router,         prefix=f"{PREFIX}/users",         tags=["Users"])
app.include_router(conversations.router, prefix=f"{PREFIX}/conversations", tags=["Conversations"])
app.include_router(documents.router,     prefix=f"{PREFIX}/documents",     tags=["Documents"])
app.include_router(webhooks.router,      prefix=f"{PREFIX}/webhooks",      tags=["Webhooks"])
app.include_router(agents.router,        prefix=f"{PREFIX}/agents",        tags=["Agents"])
app.include_router(content.router,       prefix=f"{PREFIX}/content",       tags=["Content"])
app.include_router(payments.router,      prefix=f"{PREFIX}/payments",      tags=["Payments"])
app.include_router(heygen_wh.router,     prefix="/webhooks",               tags=["Webhooks"])
app.include_router(fal_wh.router,        prefix="/webhooks",               tags=["Webhooks"])


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok", "service": "hermes-api"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=2)
