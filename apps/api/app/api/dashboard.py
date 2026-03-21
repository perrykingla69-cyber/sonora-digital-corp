from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..services.dashboard_service import build_dashboard
from schemas import DashboardResponse  # type: ignore
from security import get_current_user  # type: ignore

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return build_dashboard(db, current_user.tenant_id)
