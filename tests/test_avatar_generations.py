from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.database import AsyncSessionLocal, Base, engine, init_db
from app.db.models import AvatarGenerationJob
from app.services.rag import RagContextResult
from main import app


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def sample_request() -> dict:
    return {
        "avatarId": 1,
        "sourceImageUri": "s3://aikon-test/source/1.png",
        "style": "STUDIO",
        "gender": "MALE",
        "ageRange": "AGE_20_PLUS",
        "callbackUrl": "http://localhost:8080/internal/ai/avatar-generations/callback",
    }


def _make_mocks(rag_result: RagContextResult | None = None):
    if rag_result is None:
        rag_result = RagContextResult(context="", retrieved_feedback_ids=[])
    return (
        patch(
            "app.services.avatar_job_processor.s3.download_image",
            new_callable=AsyncMock,
            return_value=b"fake_source_bytes",
        ),
        patch(
            "app.services.avatar_job_processor.gemini_image.generate_avatar_image",
            new_callable=AsyncMock,
            return_value=b"fake_output_bytes",
        ),
        patch(
            "app.services.avatar_job_processor.s3.upload_image",
            new_callable=AsyncMock,
            return_value="s3://aikon-test/avatars/1.png",
        ),
        patch(
            "app.services.avatar_job_processor.callback.send_callback",
            new_callable=AsyncMock,
        ),
        patch(
            "app.services.avatar_job_processor.rag.retrieve_rag_context",
            new_callable=AsyncMock,
            return_value=rag_result,
        ),
    )


@pytest.mark.asyncio
async def test_create_avatar_generation_returns_accepted(sample_request):
    dl, gen, ul, cb, rag = _make_mocks()
    with dl, gen, ul, cb, rag:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/ai/avatar-generations", json=sample_request)

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "ACCEPTED"
    assert "jobId" in body


@pytest.mark.asyncio
async def test_get_job_status_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ai/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_status_found(sample_request):
    dl, gen, ul, cb, rag = _make_mocks()
    with dl, gen, ul, cb, rag:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            create_resp = await client.post("/ai/avatar-generations", json=sample_request)
            job_id = create_resp.json()["jobId"]
            status_resp = await client.get(f"/ai/jobs/{job_id}")

    assert status_resp.status_code == 200
    body = status_resp.json()
    assert body["jobId"] == job_id
    assert body["avatarId"] == 1


@pytest.mark.asyncio
async def test_avatar_generation_saves_rag_metadata(sample_request):
    dl, gen, ul, cb, rag = _make_mocks(
        RagContextResult(
            context="Use the following prior avatar feedback as guidance.",
            retrieved_feedback_ids=[1, 2],
        )
    )

    with dl, gen as gen_mock, ul, cb, rag:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            create_resp = await client.post("/ai/avatar-generations", json=sample_request)
            job_id = create_resp.json()["jobId"]

    async with AsyncSessionLocal() as session:
        job = await session.get(AvatarGenerationJob, job_id)

    assert job is not None
    assert job.rag_enabled is True
    assert job.retrieved_feedback_ids == "[1, 2]"
    assert job.prompt_text is not None
    assert job.prompt_text.startswith("Use the following prior avatar feedback as guidance.")
    gen_mock.assert_awaited_once()
    generated_prompt = gen_mock.await_args.args[1]
    assert generated_prompt == job.prompt_text
