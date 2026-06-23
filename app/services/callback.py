import logging

import httpx

from app.core.config import settings
from app.schemas.avatar import AvatarCallbackPayload

logger = logging.getLogger(__name__)


async def send_callback(callback_url: str, payload: AvatarCallbackPayload) -> None:
    headers = {}
    if settings.spring_callback_token:
        headers["X-Internal-Secret"] = settings.spring_callback_token
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                callback_url,
                json=payload.model_dump(mode="json"),
                headers=headers,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("callback 전송 실패 url=%s error=%s", callback_url, exc)
            raise
