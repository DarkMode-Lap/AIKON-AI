import asyncio
from collections.abc import AsyncGenerator

import google.generativeai as genai

from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)

model = genai.GenerativeModel("gemini-1.5-flash")


async def chat(message: str) -> str:
    response = await asyncio.to_thread(model.generate_content, message)
    return response.text


async def chat_stream(message: str) -> AsyncGenerator[str, None]:
    queue: asyncio.Queue[str | None] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def _produce() -> None:
        try:
            response = model.generate_content(message, stream=True)
            for chunk in response:
                if chunk.text:
                    loop.call_soon_threadsafe(queue.put_nowait, chunk.text)
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)

    task = asyncio.create_task(asyncio.to_thread(_produce))
    try:
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield chunk
    finally:
        await task
