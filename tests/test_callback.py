from unittest.mock import AsyncMock

import httpx
import pytest

from app.schemas.avatar import AvatarCallbackPayload, JobStatus
from app.services.callback import send_callback


@pytest.mark.asyncio
async def test_send_callback_adds_token_header(monkeypatch):
    request = httpx.Request("POST", "http://spring/internal/callback")
    post = AsyncMock(return_value=httpx.Response(200, request=request))
    client = AsyncMock()
    client.__aenter__.return_value.post = post
    monkeypatch.setattr("app.services.callback.httpx.AsyncClient", lambda timeout: client)
    monkeypatch.setattr("app.services.callback.settings.spring_callback_token", "callback-secret")

    await send_callback(
        "http://spring/internal/callback",
        AvatarCallbackPayload(
            avatarId=1,
            jobId="job-1",
            status=JobStatus.COMPLETED,
            generatedImageUri="s3://aikon/avatars/1.png",
            modelName="gemini-test",
            promptVersion="v1",
            promptText="prompt",
            durationMs=100,
            errorCode=None,
            errorMessage=None,
        ),
    )

    post.assert_awaited_once()
    assert post.await_args.kwargs["headers"] == {"X-AIKON-Callback-Token": "callback-secret"}
