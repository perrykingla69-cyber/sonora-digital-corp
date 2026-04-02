"""Conversations — historial de chats por tenant."""
from fastapi import APIRouter
from sqlalchemy import text
from app.core.database import get_tenant_session
from app.core.deps import AuthUser

router = APIRouter()


@router.get("/")
async def list_conversations(current_user: AuthUser, status: str = "open", limit: int = 50):
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("""
                SELECT id, agent_assigned, status, contact_name, created_at, updated_at
                FROM conversations
                WHERE (:status = 'all' OR status = :status)
                ORDER BY updated_at DESC
                LIMIT :limit
            """),
            {"status": status, "limit": limit},
        )
        return [dict(row._mapping) for row in r.fetchall()]


@router.get("/{conv_id}/messages")
async def get_messages(conv_id: str, current_user: AuthUser):
    async with get_tenant_session(current_user.tenant_id) as db:
        r = await db.execute(
            text("""
                SELECT id, role, content, agent, tokens_used, created_at
                FROM messages
                WHERE conversation_id = :cid
                ORDER BY created_at
            """),
            {"cid": conv_id},
        )
        return [dict(row._mapping) for row in r.fetchall()]
