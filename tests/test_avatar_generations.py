from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.database import Base, engine, init_db
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


def _make_mocks():
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
    )


@pytest.mark.asyncio
async def test_create_avatar_generation_returns_accepted(sample_request):
    dl, gen, ul, cb = _make_mocks()
    with dl, gen, ul, cb:
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
    dl, gen, ul, cb = _make_mocks()
    with dl, gen, ul, cb:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            create_resp = await client.post("/ai/avatar-generations", json=sample_request)
            job_id = create_resp.json()["jobId"]
            status_resp = await client.get(f"/ai/jobs/{job_id}")

    assert status_resp.status_code == 200
    body = status_resp.json()
    assert body["jobId"] == job_id
    assert body["avatarId"] == 1
