from unittest.mock import AsyncMock

import pytest

from app.db.database import AsyncSessionLocal, Base, engine, init_db
from app.db.models import AvatarFeedback, AvatarFeedbackReason, AvatarGenerationJob
from app.schemas.dataset import DatasetExportRequest
from app.services.dataset_export import export_dataset


@pytest.fixture
async def initialized_db():
    await init_db()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_export_dataset_returns_artifact_uris(monkeypatch, initialized_db):
    upload = AsyncMock(
        side_effect=lambda data, key, content_type="application/json": f"s3://test/{key}"
    )
    monkeypatch.setattr("app.services.dataset_export.upload_text", upload)

    async with AsyncSessionLocal() as session:
        job = AvatarGenerationJob(
            id="job-1",
            avatar_id=1,
            status="COMPLETED",
            style="STUDIO",
            gender="MALE",
            age_range="AGE_20_PLUS",
            source_image_uri="s3://aikon/source/1.png",
            callback_url="http://spring/callback",
            generated_image_uri="s3://aikon/generated/1.png",
            prompt_text="prompt",
        )
        feedback = AvatarFeedback(
            avatar_id=1,
            job_id="job-1",
            rating="LIKE",
            comment="좋음",
            training_consent=True,
            feedback_use_consent=True,
            style="STUDIO",
            gender="MALE",
            age_range="AGE_20_PLUS",
            prompt_version="v1",
            model_name="gemini-test",
            reasons=[AvatarFeedbackReason(reason="GOOD_QUALITY")],
        )
        session.add_all([job, feedback])
        await session.commit()

        response = await export_dataset(DatasetExportRequest(), session)

    assert response.status == "COMPLETED"
    assert response.exportJobId.startswith("dataset-export-")
    assert response.trainCount == 1
    assert response.evalCount == 0
    assert response.trainUri.endswith("/train.jsonl")
    assert response.evalUri.endswith("/eval.jsonl")
    assert response.manifestUri.endswith("/manifest.json")
    assert upload.await_count == 3


@pytest.mark.asyncio
async def test_export_dataset_default_min_rating_excludes_dislike(monkeypatch, initialized_db):
    uploaded: dict[str, str] = {}

    async def upload(data: str, key: str, content_type: str = "application/json") -> str:
        uploaded[key] = data
        return f"s3://test/{key}"

    monkeypatch.setattr("app.services.dataset_export.upload_text", upload)

    async with AsyncSessionLocal() as session:
        session.add_all(
            [
                AvatarGenerationJob(
                    id="like-job",
                    avatar_id=1,
                    status="COMPLETED",
                    style="STUDIO",
                    gender="MALE",
                    age_range="AGE_20_PLUS",
                    source_image_uri="s3://aikon/source/1.png",
                    callback_url="http://spring/callback",
                    generated_image_uri="s3://aikon/generated/1.png",
                    prompt_text="prompt",
                ),
                AvatarGenerationJob(
                    id="dislike-job",
                    avatar_id=2,
                    status="COMPLETED",
                    style="STUDIO",
                    gender="MALE",
                    age_range="AGE_20_PLUS",
                    source_image_uri="s3://aikon/source/2.png",
                    callback_url="http://spring/callback",
                    generated_image_uri="s3://aikon/generated/2.png",
                    prompt_text="prompt",
                ),
                AvatarFeedback(
                    avatar_id=1,
                    job_id="like-job",
                    rating="LIKE",
                    comment="좋음",
                    training_consent=True,
                    feedback_use_consent=True,
                    style="STUDIO",
                    gender="MALE",
                    age_range="AGE_20_PLUS",
                ),
                AvatarFeedback(
                    avatar_id=2,
                    job_id="dislike-job",
                    rating="DISLIKE",
                    comment="별로",
                    training_consent=True,
                    feedback_use_consent=True,
                    style="STUDIO",
                    gender="MALE",
                    age_range="AGE_20_PLUS",
                ),
            ]
        )
        await session.commit()

        response = await export_dataset(DatasetExportRequest(), session)

    assert response.trainCount == 1
    assert response.evalCount == 0
    eval_key = next(key for key in uploaded if key.endswith("/eval.jsonl"))
    assert uploaded[eval_key] == ""
