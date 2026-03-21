from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..services.alert_service import get_or_create_alert_config, serialize_alert_config, update_alert_config
from security import get_current_user  # type: ignore


from ..schemas import AlertaConfigUpdate

router = APIRouter(tags=["Alertas"])


@router.get("/alertas/config")
async def get_alerta_config(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    config = get_or_create_alert_config(db, str(current_user.tenant_id), str(current_user.id))
    return serialize_alert_config(config)


@router.patch("/alertas/config")
async def patch_alerta_config(body: AlertaConfigUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return update_alert_config(db, str(current_user.tenant_id), str(current_user.id), body.model_dump(exclude_none=True))
