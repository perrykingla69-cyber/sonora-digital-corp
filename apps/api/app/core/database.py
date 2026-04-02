"""
Database — Multi-tenant con RLS vía SET app.current_tenant_id
Cada request setea el tenant ANTES de cualquier query.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text, event
from contextlib import asynccontextmanager
from uuid import UUID
from typing import AsyncGenerator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def init_db():
    async with engine.begin() as conn:
        logger.info("Database connection established")


@asynccontextmanager
async def get_tenant_session(tenant_id: UUID) -> AsyncGenerator[AsyncSession, None]:
    """
    Sesión con RLS activo para el tenant.
    SIEMPRE usar este context manager en endpoints — nunca get_db directamente.
    """
    async with AsyncSessionLocal() as session:
        # Activar RLS para este tenant
        await session.execute(
            text(f"SET LOCAL app.current_tenant_id = '{str(tenant_id)}'"),
        )
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Solo para operaciones de sistema (sin tenant). NO usar en endpoints normales."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
