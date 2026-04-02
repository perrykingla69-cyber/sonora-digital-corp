"""Documents — facturas, CFDIs, reportes contables."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import text
from app.core.database import get_tenant_session
from app.core.deps import AuthUser

router = APIRouter()


class CreateDocumentRequest(BaseModel):
    type: str
    folio: Optional[str] = None
    period_year: Optional[int] = None
    period_month: Optional[int] = None
    amount: Optional[float] = None
    currency: str = "MXN"
    data: dict = {}


@router.get("/")
async def list_documents(
    current_user: AuthUser,
    type: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    limit: int = 100,
):
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("""
                SELECT id, type, folio, period_year, period_month, amount, currency, status, created_at
                FROM documents
                WHERE (:type IS NULL OR type = :type)
                AND (:year IS NULL OR period_year = :year)
                AND (:month IS NULL OR period_month = :month)
                ORDER BY created_at DESC
                LIMIT :limit
            """),
            {"type": type, "year": year, "month": month, "limit": limit},
        )
        return [dict(row._mapping) for row in r.fetchall()]


@router.post("/", status_code=201)
async def create_document(body: CreateDocumentRequest, current_user: AuthUser):
    import json
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("""
                INSERT INTO documents (tenant_id, type, folio, period_year, period_month,
                    amount, currency, data, created_by)
                VALUES (current_tenant_id(), :type, :folio, :year, :month,
                    :amount, :currency, :data::jsonb, :uid)
                RETURNING id
            """),
            {
                "type": body.type,
                "folio": body.folio,
                "year": body.period_year,
                "month": body.period_month,
                "amount": body.amount,
                "currency": body.currency,
                "data": json.dumps(body.data),
                "uid": str(current_user.user_id),
            },
        )
        doc_id = r.scalar_one()
    return {"id": str(doc_id)}
