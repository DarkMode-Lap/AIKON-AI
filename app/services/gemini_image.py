import asyncio
import base64

from google import genai
from google.genai import types

from app.core.config import settings

_client = genai.Client(api_key=settings.gemini_api_key)


def _generate_sync(source_bytes: bytes, prompt: str) -> bytes:
    response = _client.models.generate_content(
        model=settings.gemini_image_model,
        contents=[
            types.Part.from_bytes(data=source_bytes, mime_type="image/png"),
            types.Part.from_text(text=prompt),
        ],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return base64.b64decode(part.inline_data.data)
    raise ValueError("Gemini 응답에 이미지 데이터가 없습니다")


async def generate_avatar_image(source_bytes: bytes, prompt: str) -> bytes:
    return await asyncio.to_thread(_generate_sync, source_bytes, prompt)
