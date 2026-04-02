"""Tenant management — solo owners/admins del sistema."""
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text
from app.core.database import get_db, get_tenant_session
from app.core.deps import AuthUser
from app.core.security import hash_password

router = APIRouter()


class CreateTenantRequest(BaseModel):
    slug: str
    name: str
    plan: str = "starter"
    owner_email: str
    owner_password: str
    owner_name: str


@router.post("/", status_code=201)
async def create_tenant(body: CreateTenantRequest):
    """Crear nuevo tenant (onboarding). Endpoint público con validación."""
    async with get_db() as db:
        existing = await db.execute(
            text("SELECT id FROM tenants WHERE slug = :slug"), {"slug": body.slug}
        )
        if existing.fetchone():
            from fastapi import HTTPException
            raise HTTPException(400, "Slug ya existe")

        result = await db.execute(
            text("INSERT INTO tenants (slug, name, plan) VALUES (:slug, :name, :plan) RETURNING id"),
            {"slug": body.slug, "name": body.name, "plan": body.plan},
        )
        tenant_id = result.scalar_one()

    async with get_tenant_session(tenant_id) as db:
        await db.execute(
            text("""
                INSERT INTO users (tenant_id, email, password_hash, full_name, role)
                VALUES (:tid, :email, :pwd, :name, 'owner')
            """),
            {
                "tid": str(tenant_id),
                "email": body.owner_email,
                "pwd": hash_password(body.owner_password),
                "name": body.owner_name,
            },
        )

    return {"tenant_id": str(tenant_id), "slug": body.slug}


@router.get("/me")
async def get_my_tenant(current_user: AuthUser):
    async with get_tenant_session(current_user.tenant_id) as db:
        result = await db.execute(
            text("SELECT id, slug, name, plan, settings, created_at FROM tenants WHERE id = current_tenant_id()")
        )
        tenant = result.fetchone()
    return dict(tenant._mapping)
