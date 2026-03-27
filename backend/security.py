"""Auth y seguridad — JWT + bcrypt."""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY no configurada en variables de entorno")
SYSTEM_TOKEN = os.getenv("SYSTEM_TOKEN", "")
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 30

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(user_id: str, extra: dict) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS),
        **extra,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    from models import Usuario

    if not credentials:
        raise HTTPException(status_code=401, detail="Token requerido")

    token = credentials.credentials

    # SYSTEM_TOKEN para integraciones internas (N8N, etc.)
    if SYSTEM_TOKEN and token == SYSTEM_TOKEN:
        return {"id": "system", "rol": "ceo", "tenant_id": None, "system": True}

    payload = decode_token(token)
    user = db.query(Usuario).filter(Usuario.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user


def require_role(*roles: str):
    def _check(current_user=Depends(get_current_user)):
        rol = current_user.rol if hasattr(current_user, "rol") else current_user.get("rol")
        if rol not in roles:
            raise HTTPException(status_code=403, detail=f"Rol requerido: {', '.join(roles)}")
        return current_user
    return _check
