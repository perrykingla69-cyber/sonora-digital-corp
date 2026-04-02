"""
Dependencias FastAPI — extrae tenant_id del JWT y activa RLS
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
from typing import Annotated

from app.core.security import decode_token
from app.core.redis import redis_client

bearer = HTTPBearer()


class CurrentUser:
    def __init__(self, user_id: UUID, tenant_id: UUID, role: str, jti: str):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role = role
        self.jti = jti


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> CurrentUser:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    jti = payload.get("jti", "")
    # Verificar que el token no fue revocado (logout)
    if await redis_client.get(f"revoked:{jti}"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revocado")

    return CurrentUser(
        user_id=UUID(payload["sub"]),
        tenant_id=UUID(payload["tid"]),
        role=payload["role"],
        jti=jti,
    )


def require_role(*roles: str):
    async def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos")
        return user
    return checker


# Tipos útiles
AuthUser = Annotated[CurrentUser, Depends(get_current_user)]
OwnerUser = Annotated[CurrentUser, Depends(require_role("owner", "admin"))]
