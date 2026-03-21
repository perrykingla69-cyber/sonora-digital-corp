from __future__ import annotations

import secrets
import string
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core import legacy  # noqa: F401
from ..integrations.whatsapp_client import WhatsAppClient
from models import Usuario  # type: ignore
from security import create_token, hash_password, verify_password  # type: ignore


def login_user(db: Session, email: str, password: str) -> dict[str, Any]:
    usuario = db.query(Usuario).filter(Usuario.email == email, Usuario.activo == True).first()
    if not usuario or not verify_password(password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    token = create_token(str(usuario.id), extra={"tenant": str(usuario.tenant_id), "rol": usuario.rol})
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}


def register_user(db: Session, body) -> Any:
    if db.query(Usuario).filter(Usuario.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    usuario = Usuario(
        tenant_id=body.tenant_id,
        email=body.email,
        password_hash=hash_password(body.password),
        nombre=body.nombre,
        rol=body.rol,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def reset_password(db: Session, email: str, whatsapp_client: WhatsAppClient) -> dict[str, Any]:
    normalized = email.strip().lower()
    if not normalized:
        raise HTTPException(status_code=400, detail="Email requerido")
    usuario = db.query(Usuario).filter(Usuario.email == normalized).first()
    if not usuario:
        return {"ok": True, "mensaje": "Si el correo existe, recibirás la nueva contraseña por WhatsApp"}

    chars = string.ascii_letters + string.digits
    temp_pass = "".join(secrets.choice(chars) for _ in range(10))
    usuario.password_hash = hash_password(temp_pass)
    db.commit()

    wa_sent = False
    wa_numbers = {
        "cp.nathalyhermosillo@gmail.com": "526622681111",
        "marco@fourgea.mx": "526623538272",
    }
    wa_num = wa_numbers.get(normalized)
    if wa_num:
        try:
            whatsapp_client.send_text(
                wa_num,
                f"🔐 Mystic — Contraseña temporal: *{temp_pass}*\nCámbiala después de ingresar.",
            )
            wa_sent = True
        except Exception:
            wa_sent = False

    return {
        "ok": True,
        "wa_sent": wa_sent,
        "mensaje": "Contraseña enviada por WhatsApp" if wa_sent else "Contacta a tu administrador: sonoradigitalcorp@gmail.com",
    }
