from __future__ import annotations

from sqlalchemy.orm import Session

from ..core import legacy  # noqa: F401
from models import AlertaConfig  # type: ignore


def get_or_create_alert_config(db: Session, tenant_id: str, user_id: str):
    config = db.query(AlertaConfig).filter(AlertaConfig.tenant_id == tenant_id).first()
    if not config:
        config = AlertaConfig(tenant_id=tenant_id)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def serialize_alert_config(config: AlertaConfig) -> dict:
    return {
        "activo": config.activo,
        "hora_manana": config.hora_manana,
        "hora_tarde": config.hora_tarde,
        "chat_id_telegram": config.chat_id_telegram,
    }


def update_alert_config(db: Session, tenant_id: str, user_id: str, payload: dict) -> dict:
    config = get_or_create_alert_config(db, tenant_id, user_id)
    for campo, valor in payload.items():
        if hasattr(config, campo):
            setattr(config, campo, valor)
    db.commit()
    db.refresh(config)
    return serialize_alert_config(config)
