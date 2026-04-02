"""Users — CRUD dentro del tenant."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from app.core.database import get_tenant_session
from app.core.deps import AuthUser, OwnerUser
from app.core.security import hash_password

router = APIRouter()


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
