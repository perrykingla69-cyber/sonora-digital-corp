"""Auth — Login, refresh, logout con revocación JWT."""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from datetime import timedelta

from app.core.database import get_db, get_tenant_session
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.redis import redis_client
from app.core.deps import AuthUser

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_slug: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    async with get_db() as db:
        # Buscar tenant
        t = await db.execute(
            text("SELECT id FROM tenants WHERE slug = :slug AND is_active = true"),
            {"slug": body.tenant_slug},
        )
        tenant = t.fetchone()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant no encontrado")

    async with get_tenant_session(tenant.id) as db:
        u = await db.execute(
            text("SELECT id, password_hash, role FROM users WHERE email = :email AND is_active = true"),
            {"email": body.email},
        )
        user = u.fetchone()

    if not user or not verify_password(body.password, user.password_hash):
        # Delay para mitigar brute force
        import asyncio; await asyncio.sleep(0.5)
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    access = create_access_token(user.id, tenant.id, user.role)
    refresh = create_refresh_token(user.id, tenant.id)

    # Actualizar last_login
    async with get_tenant_session(tenant.id) as db:
        await db.execute(
            text("UPDATE users SET last_login_at = NOW() WHERE id = :uid"),
            {"uid": str(user.id)},
        )

    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/logout")
async def logout(current_user: AuthUser):
    # Revocar token en Redis (TTL = tiempo restante del token)
    payload = decode_token  # ya validado en deps
    await redis_client.setex(f"revoked:{current_user.jti}", 3600, "1")
    return {"detail": "Sesión cerrada"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str):
    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token incorrecto")

    from uuid import UUID
    user_id = UUID(payload["sub"])
    tenant_id = UUID(payload["tid"])

    async with get_tenant_session(tenant_id) as db:
        u = await db.execute(
            text("SELECT role FROM users WHERE id = :uid AND is_active = true"),
            {"uid": str(user_id)},
        )
        user = u.fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    access = create_access_token(user_id, tenant_id, user.role)
    new_refresh = create_refresh_token(user_id, tenant_id)
    return TokenResponse(access_token=access, refresh_token=new_refresh)
