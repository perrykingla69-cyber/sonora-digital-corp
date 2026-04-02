from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..db.session import get_db

router = APIRouter(tags=["Sistema"])


@router.get("/")
async def root():
    return {"system": "MYSTIC API v2", "status": "ok"}


@router.get("/health")
async def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "online",
        "db": "ok" if db_ok else "error",
        "timestamp": datetime.utcnow().isoformat(),
    }
