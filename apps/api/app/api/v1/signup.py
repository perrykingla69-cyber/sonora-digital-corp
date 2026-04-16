"""
Signup / User Management — Fase 1 SaaS
Registro público con auto-creación de tenant.
"""

import secrets
import re
import unicodedata
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import text

from app.core.database import get_db, get_tenant_session
from app.core.security import hash_password, create_access_token
from app.core.deps import AuthUser

router = APIRouter()


# ── Helpers ───────────────────────────────────────────────────

def _slugify(text_: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text_.lower())
    ascii_ = nfkd.encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_).strip("-")[:50]


def _generate_api_key() -> str:
    return f"sdc_{secrets.token_urlsafe(32)}"


# ── Schemas ───────────────────────────────────────────────────

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str


class SignupResponse(BaseModel):
    user_id: str
    email: str
    jwt_token: str
    tenant_id: str
    tenant_slug: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_slug: str | None = None  # Opcional — si no se da, busca por email


class LoginResponse(BaseModel):
    jwt_token: str
    user_id: str
    tenant_id: str
    tenant_slug: str


class ApiKeyResponse(BaseModel):
    key: str
    created_at: str | None
    last_used: str | None


# ── Endpoints ─────────────────────────────────────────────────

@router.post("/signup", response_model=SignupResponse, status_code=201)
async def signup(body: SignupRequest):
    """
    Registro nuevo usuario.
    Auto-crea tenant a partir de company_name.
    Devuelve JWT listo para usar.
    """
    # Validar contraseña
    if len(body.password) < 8:
        raise HTTPException(400, "La contraseña debe tener al menos 8 caracteres")

    # Verificar email único
    async with get_db() as db:
        dup = await db.execute(
            text("SELECT id FROM users WHERE email = :email LIMIT 1"),
            {"email": body.email},
        )
        if dup.fetchone():
            raise HTTPException(400, "El email ya está registrado")

    # Generar slug único para el tenant
    base_slug = _slugify(body.company_name)
    slug = base_slug
    async with get_db() as db:
        for i in range(1, 20):
            exists = await db.execute(
                text("SELECT id FROM tenants WHERE slug = :s"), {"s": slug}
            )
            if not exists.fetchone():
                break
            slug = f"{base_slug}-{i}"
        else:
            slug = f"{base_slug}-{secrets.token_hex(3)}"

    # Crear tenant
    async with get_db() as db:
        t = await db.execute(
            text("""
                INSERT INTO tenants (slug, name, plan)
                VALUES (:slug, :name, 'free')
                RETURNING id
            """),
            {"slug": slug, "name": body.company_name},
        )
        tenant_id = t.scalar_one()
        await db.commit()

    # Crear usuario owner
    api_key = _generate_api_key()
    pwd_hash = hash_password(body.password)

    async with get_tenant_session(tenant_id) as db:
        u = await db.execute(
            text("""
                INSERT INTO users
                    (tenant_id, email, password_hash, full_name, role,
                     company_name, subscription_plan, api_key, api_key_created_at, is_active)
                VALUES
                    (:tid, :email, :pwd, :name, 'owner',
                     :company, 'free', :api_key, NOW(), true)
                RETURNING id
            """),
            {
                "tid": str(tenant_id),
                "email": body.email,
                "pwd": pwd_hash,
                "name": body.full_name,
                "company": body.company_name,
                "api_key": api_key,
            },
        )
        user_id = u.scalar_one()

        # Crear suscripción free
        await db.execute(
            text("""
                INSERT INTO subscriptions
                    (user_id, tenant_id, plan, status, current_period_start, current_period_end)
                VALUES
                    (:uid, :tid, 'free', 'active', CURRENT_DATE, CURRENT_DATE + INTERVAL '30 days')
            """),
            {"uid": str(user_id), "tid": str(tenant_id)},
        )

    jwt_token = create_access_token(user_id, tenant_id, "owner")

    return SignupResponse(
        user_id=str(user_id),
        email=body.email,
        jwt_token=jwt_token,
        tenant_id=str(tenant_id),
        tenant_slug=slug,
    )


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest):
    """
    Login con email + password.
    tenant_slug opcional — si no se da, busca el primer tenant del usuario.
    """
    from app.core.security import verify_password

    # Buscar usuario por email (cross-tenant search en tabla global)
    async with get_db() as db:
        if body.tenant_slug:
            t = await db.execute(
                text("SELECT id FROM tenants WHERE slug = :slug AND is_active = true"),
                {"slug": body.tenant_slug},
            )
            tenant = t.fetchone()
            if not tenant:
                raise HTTPException(404, "Tenant no encontrado")
            tenant_id = tenant.id
        else:
            # Buscar tenant por email del usuario
            r = await db.execute(
                text("""
                    SELECT u.id, u.password_hash, u.role, u.tenant_id, t.slug
                    FROM users u
                    JOIN tenants t ON t.id = u.tenant_id
                    WHERE u.email = :email AND u.is_active = true
                    LIMIT 1
                """),
                {"email": body.email},
            )
            row = r.fetchone()
            if not row:
                import asyncio; await asyncio.sleep(0.5)
                raise HTTPException(401, "Credenciales incorrectas")
            if not verify_password(body.password, row.password_hash):
                import asyncio; await asyncio.sleep(0.5)
                raise HTTPException(401, "Credenciales incorrectas")

            # Actualizar last_login
            async with get_tenant_session(row.tenant_id) as db2:
                await db2.execute(
                    text("UPDATE users SET last_login = NOW() WHERE id = :uid"),
                    {"uid": str(row.id)},
                )

            jwt = create_access_token(row.id, row.tenant_id, row.role)
            return LoginResponse(
                jwt_token=jwt,
                user_id=str(row.id),
                tenant_id=str(row.tenant_id),
                tenant_slug=row.slug,
            )

    # Buscar con tenant conocido
    async with get_tenant_session(tenant_id) as db:
        u = await db.execute(
            text("""
                SELECT id, password_hash, role
                FROM users
                WHERE email = :email AND is_active = true
                LIMIT 1
            """),
            {"email": body.email},
        )
        user = u.fetchone()

    if not user:
        import asyncio; await asyncio.sleep(0.5)
        raise HTTPException(401, "Credenciales incorrectas")

    from app.core.security import verify_password as _vp
    if not _vp(body.password, user.password_hash):
        import asyncio; await asyncio.sleep(0.5)
        raise HTTPException(401, "Credenciales incorrectas")

    # Actualizar last_login
    async with get_tenant_session(tenant_id) as db:
        await db.execute(
            text("UPDATE users SET last_login = NOW() WHERE id = :uid"),
            {"uid": str(user.id)},
        )
        t_slug = body.tenant_slug

    jwt = create_access_token(user.id, tenant_id, user.role)
    return LoginResponse(
        jwt_token=jwt,
        user_id=str(user.id),
        tenant_id=str(tenant_id),
        tenant_slug=t_slug or "",
    )


@router.get("/me")
async def get_me(current_user: AuthUser):
    """Perfil completo del usuario autenticado."""
    async with get_tenant_session(current_user.tenant_id) as db:
        u = await db.execute(
            text("""
                SELECT
                    u.id, u.email, u.full_name, u.role, u.company_name,
                    u.subscription_plan, u.api_key_created_at, u.api_key_last_used,
                    u.last_login, u.is_active, u.created_at
                FROM users u
                WHERE u.id = :uid
            """),
            {"uid": str(current_user.user_id)},
        )
        user = u.fetchone()
        if not user:
            raise HTTPException(404, "Usuario no encontrado")

        # Bots del usuario
        b = await db.execute(
            text("""
                SELECT id, name, channel, status, created_at
                FROM bots
                WHERE user_id = :uid
                ORDER BY created_at DESC
            """),
            {"uid": str(current_user.user_id)},
        )
        bots = [dict(r._mapping) for r in b.fetchall()]

        # Subscripción activa
        s = await db.execute(
            text("""
                SELECT plan, status, current_period_start, current_period_end
                FROM subscriptions
                WHERE user_id = :uid AND status = 'active'
                LIMIT 1
            """),
            {"uid": str(current_user.user_id)},
        )
        sub = s.fetchone()

    return {
        "user": {
            **{k: str(v) if hasattr(v, 'hex') else v
               for k, v in dict(user._mapping).items()},
        },
        "subscription": dict(sub._mapping) if sub else None,
        "bots": [
            {k: str(v) if hasattr(v, 'hex') else
             v.isoformat() if hasattr(v, 'isoformat') else v
             for k, v in b.items()}
            for b in bots
        ],
    }


@router.get("/me/api-keys", response_model=list[ApiKeyResponse])
async def get_api_keys(current_user: AuthUser):
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("""
                SELECT api_key, api_key_created_at, api_key_last_used
                FROM users WHERE id = :uid
            """),
            {"uid": str(current_user.user_id)},
        )
        row = r.fetchone()
    if not row or not row.api_key:
        return []
    return [ApiKeyResponse(
        key=row.api_key,
        created_at=row.api_key_created_at.isoformat() if row.api_key_created_at else None,
        last_used=row.api_key_last_used.isoformat() if row.api_key_last_used else None,
    )]


@router.post("/me/regenerate-api-key")
async def regenerate_api_key(current_user: AuthUser):
    new_key = _generate_api_key()
    async with get_tenant_session(current_user.tenant_id) as db:
        await db.execute(
            text("""
                UPDATE users
                SET api_key = :key, api_key_created_at = NOW(), api_key_last_used = NULL
                WHERE id = :uid
            """),
            {"key": new_key, "uid": str(current_user.user_id)},
        )
    return {"key": new_key}
