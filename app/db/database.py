from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url, echo=settings.debug)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if engine.dialect.name == "sqlite":
            result = await conn.execute(text("PRAGMA table_info(avatar_generation_jobs)"))
            columns = {row[1] for row in result.fetchall()}
            if "rag_enabled" not in columns:
                await conn.execute(
                    text(
                        "ALTER TABLE avatar_generation_jobs "
                        "ADD COLUMN rag_enabled BOOLEAN NOT NULL DEFAULT 0"
                    )
                )
            if "retrieved_feedback_ids" not in columns:
                await conn.execute(
                    text(
                        "ALTER TABLE avatar_generation_jobs "
                        "ADD COLUMN retrieved_feedback_ids TEXT"
                    )
                )
            if "retrieval_query" not in columns:
                await conn.execute(
                    text("ALTER TABLE avatar_generation_jobs ADD COLUMN retrieval_query TEXT")
                )
            if "retrieval_scores" not in columns:
                await conn.execute(
                    text("ALTER TABLE avatar_generation_jobs ADD COLUMN retrieval_scores TEXT")
                )
            if "callback_status" not in columns:
                await conn.execute(
                    text(
                        "ALTER TABLE avatar_generation_jobs "
                        "ADD COLUMN callback_status VARCHAR(20)"
                    )
                )
            if "callback_error" not in columns:
                await conn.execute(
                    text("ALTER TABLE avatar_generation_jobs ADD COLUMN callback_error TEXT")
                )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
