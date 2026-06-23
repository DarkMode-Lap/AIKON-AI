from collections.abc import AsyncGenerator

import google.generativeai as genai

from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)

model = genai.GenerativeModel("gemini-1.5-flash")


async def chat(message: str) -> str:
    response = await model.generate_content_async(message)
    return response.text


async def chat_stream(message: str) -> AsyncGenerator[str, None]:
    response = await model.generate_content_async(message, stream=True)
    async for chunk in response:
        if chunk.text:
            yield chunk.text
