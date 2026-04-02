from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core import legacy  # noqa: F401
from ..db.session import get_db
from ..integrations.whatsapp_client import WhatsAppClient
from ..services.auth_service import login_user, register_user, reset_password
from ..schemas import LoginRequest, LoginResponse, UsuarioCreate, UsuarioResponse
from security import get_current_user  # type: ignore

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db, body.email, body.password)


@router.post("/registro", response_model=UsuarioResponse)
async def registro(body: UsuarioCreate, db: Session = Depends(get_db)):
    return register_user(db, body)


@router.get("/me", response_model=UsuarioResponse)
async def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/forgot-password")
async def forgot_password(body: dict, db: Session = Depends(get_db)):
    return reset_password(db, body.get("email", ""), WhatsAppClient())
