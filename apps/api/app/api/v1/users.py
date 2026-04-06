"""Users — CRUD dentro del tenant."""
import re
import secrets
import unicodedata

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import text

from app.core.database import get_db, get_tenant_session
from app.core.deps import AuthUser, OwnerUser
from app.core.security import hash_password, create_access_token

router = APIRouter()


# ── Helpers ──────────────────────────────────────────────────

def _slugify(text_: str) -> str:
    """'Juan García Músico' → 'juan-garcia-musico'"""
    nfkd = unicodedata.normalize("NFKD", text_.lower())
    ascii_ = nfkd.encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_).strip("-")[:60]


# ── Onboarding vía Telegram ───────────────────────────────────

class TelegramOnboardRequest(BaseModel):
    chat_id: str           # ID de Telegram del usuario
    full_name: str         # Nombre completo
    business_type: str     # restaurante, contador, musico, etc.
    slug: str | None = None  # Si viene vacío, se genera desde full_name


@router.post("/onboard-telegram", status_code=201)
async def onboard_telegram(body: TelegramOnboardRequest):
    """
    Registro de nuevo usuario desde flujo de Telegram.
    Crea tenant + user owner + devuelve JWT + slug de página.
    Endpoint público — no requiere auth.
    """
    # Verificar que el chat_id no esté ya registrado
    async with get_db() as db:
        dup = await db.execute(
            text("SELECT id FROM users WHERE telegram_chat_id = :cid LIMIT 1"),
            {"cid": body.chat_id},
        )
        if dup.fetchone():
            raise HTTPException(400, "Este Telegram ya está registrado")

    # Generar slug único
    base_slug = body.slug or _slugify(f"{body.full_name}-{body.business_type}")
    slug = base_slug
    async with get_db() as db:
        for i in range(1, 10):
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
        r = await db.execute(
            text("""
                INSERT INTO tenants (slug, name, plan)
                VALUES (:slug, :name, 'starter')
                RETURNING id
            """),
            {"slug": slug, "name": body.full_name},
        )
        tenant_id = r.scalar_one()
        await db.commit()

    # Crear usuario owner dentro del tenant
    fake_email = f"tg-{body.chat_id}@hermes.internal"
    fake_pwd = hash_password(secrets.token_hex(16))

    async with get_tenant_session(tenant_id) as db:
        r = await db.execute(
            text("""
                INSERT INTO users
                    (tenant_id, email, password_hash, full_name, role,
                     telegram_chat_id, tokens_balance, plan, slug)
                VALUES
                    (:tid, :email, :pwd, :name, 'owner',
                     :chat_id, 100, 'starter', :slug)
                RETURNING id
            """),
            {
                "tid": str(tenant_id),
                "email": fake_email,
                "pwd": fake_pwd,
                "name": body.full_name,
                "chat_id": body.chat_id,
                "slug": slug,
            },
        )
        user_id = r.scalar_one()
        await db.commit()

    # Generar JWT
    access_token = create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        role="owner",
    )

    return {
        "slug": slug,
        "tenant_id": str(tenant_id),
        "user_id": str(user_id),
        "access_token": access_token,
        "dashboard_url": f"https://sonoradigitalcorp.com/user/{slug}",
    }


@router.get("/profile/{slug}")
async def get_profile_by_slug(slug: str):
    """
    Perfil público del usuario por slug.
    Devuelve datos para renderizar la página /user/[slug].
    """
    async with get_db() as db:
        r = await db.execute(
            text("""
                SELECT
                    u.full_name,
                    u.avatar_url,
                    u.tokens_balance,
                    u.plan,
                    u.slug,
                    u.created_at,
                    t.name  AS tenant_name,
                    t.slug  AS tenant_slug,
                    COALESCE(
                        (SELECT COUNT(*) FROM conversations cv
                         JOIN tenants tt ON tt.id = cv.tenant_id
                         WHERE tt.slug = :slug),
                    0) AS total_conversations,
                    COALESCE(
                        (SELECT COUNT(*) FROM assets a
                         JOIN users uu ON uu.id = a.user_id
                         WHERE uu.slug = :slug AND a.status = 'ready'),
                    0) AS total_assets
                FROM users u
                JOIN tenants t ON t.id = u.tenant_id
                WHERE u.slug = :slug
                LIMIT 1
            """),
            {"slug": slug},
        )
        row = r.fetchone()

    if not row:
        raise HTTPException(404, "Perfil no encontrado")

    data = dict(row._mapping)

    # Calcular nivel/score
    score = (data["total_conversations"] * 10) + (data["total_assets"] * 25)
    if score < 100:
        level, level_name = 1, "Aprendiz"
    elif score < 500:
        level, level_name = 2, "Activo"
    elif score < 1500:
        level, level_name = 3, "Pro"
    else:
        level, level_name = 4, "Experto"

    data["score"] = score
    data["level"] = level
    data["level_name"] = level_name
    data["created_at"] = data["created_at"].isoformat() if data.get("created_at") else None
    return data


@router.get("/me")
async def get_me(current_user: AuthUser):
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("SELECT id, email, full_name, role, last_login_at FROM users WHERE id = :uid"),
            {"uid": str(current_user.user_id)},
        )
        user = r.fetchone()
    return dict(user._mapping)


@router.get("/")
async def list_users(current_user: OwnerUser):
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("SELECT id, email, full_name, role, is_active, last_login_at FROM users ORDER BY created_at")
        )
        return [dict(row._mapping) for row in r.fetchall()]


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "member"


@router.post("/", status_code=201)
async def create_user(body: CreateUserRequest, current_user: OwnerUser):
    async with get_tenant_session(current_user.tenant_id) as db:
        await db.execute(
            text("""
                INSERT INTO users (tenant_id, email, password_hash, full_name, role)
                VALUES (current_tenant_id(), :email, :pwd, :name, :role)
            """),
            {"email": body.email, "pwd": hash_password(body.password), "name": body.full_name, "role": body.role},
        )
    return {"detail": "Usuario creado"}
