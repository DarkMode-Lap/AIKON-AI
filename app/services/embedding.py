from __future__ import annotations

import asyncio
import threading

from google import genai

from app.core.config import settings

_client: genai.Client | None = None
_client_lock = threading.Lock()


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


async def embed_text(text: str) -> list[float]:
    def _embed() -> list[float]:
        response = _get_client().models.embed_content(
            model="text-embedding-004",
            contents=text,
        )
        if not response.embeddings:
            raise ValueError("Gemini embedding 응답에 embeddings가 없습니다")
        values = response.embeddings[0].values
        if values is None:
            raise ValueError("Gemini embedding 응답에 vector 값이 없습니다")
        return list(values)

    return await asyncio.to_thread(_embed)
