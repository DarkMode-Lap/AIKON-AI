import json

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.database import AsyncSessionLocal, Base, engine, init_db
from app.db.models import AvatarFeedback, AvatarGenerationJob
from main import app


@pytest.fixture
async def initialized_db():
    await init_db()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_rag_impact_metrics(initialized_db):
    async with AsyncSessionLocal() as session:
        session.add_all(
            [
                AvatarGenerationJob(
                    id="rag-job",
                    avatar_id=1,
                    status="COMPLETED",
                    style="STUDIO",
                    gender="MALE",
                    age_range="AGE_20_PLUS",
                    source_image_uri="s3://aikon/source/1.png",
                    callback_url="http://spring/callback",
                    rag_enabled=True,
                    retrieval_scores=json.dumps([0.7, 0.5]),
                ),
                AvatarGenerationJob(
                    id="plain-job",
                    avatar_id=1,
                    status="COMPLETED",
                    style="STUDIO",
                    gender="MALE",
                    age_range="AGE_20_PLUS",
                    source_image_uri="s3://aikon/source/2.png",
                    callback_url="http://spring/callback",
                    rag_enabled=False,
                ),
                AvatarFeedback(
                    avatar_id=1,
                    job_id="rag-job",
                    rating="LIKE",
                    comment=None,
                    training_consent=True,
                    feedback_use_consent=True,
                    style="STUDIO",
                    gender="MALE",
                    age_range="AGE_20_PLUS",
                ),
                AvatarFeedback(
                    avatar_id=2,
                    job_id="plain-job",
                    rating="DISLIKE",
                    comment=None,
                    training_consent=True,
                    feedback_use_consent=True,
                    style="STUDIO",
                    gender="MALE",
                    age_range="AGE_20_PLUS",
                ),
            ]
        )
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/admin/metrics/rag-impact")

    assert response.status_code == 200
    body = response.json()
    assert body["totalCount"] == 2
    assert body["ragEnabledCount"] == 1
    assert body["ragHitRate"] == 0.5
    assert body["ragLikeRate"] == 1.0
    assert body["nonRagLikeRate"] == 0.0
    assert body["avgRetrievalScore"] == 0.6
