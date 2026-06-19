import base64

from google import genai
from google.genai import types

from app.core.config import settings

_client = genai.Client(api_key=settings.gemini_api_key)


async def generate_avatar_image(source_bytes: bytes, prompt: str) -> bytes:
    response = await _client.aio.models.generate_content(
        model=settings.gemini_image_model,
        contents=[
            types.Part.from_bytes(data=source_bytes, mime_type="image/png"),
            types.Part.from_text(text=prompt),
        ],
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )
    if not response.candidates:
        raise ValueError(
            "Gemini 응답에 후보(candidates)가 없습니다. 안전 필터에 의해 차단되었을 수 있습니다."
        )
    candidate = response.candidates[0]
    if not candidate.content or not candidate.content.parts:
        raise ValueError("Gemini 응답 후보에 콘텐츠 또는 파트가 없습니다.")
    for part in candidate.content.parts:
        if part.inline_data is not None:
            return base64.b64decode(part.inline_data.data)
    raise ValueError("Gemini 응답에 이미지 데이터가 없습니다")
