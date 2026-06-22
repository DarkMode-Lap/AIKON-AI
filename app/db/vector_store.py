from __future__ import annotations

import asyncio
import logging
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

VECTOR_SIZE = 768

_client: AsyncQdrantClient | None = None
_collection_ready = False
_collection_lock = asyncio.Lock()


def _get_client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        _client = AsyncQdrantClient(url=settings.qdrant_url)
    return _client


async def ensure_feedback_collection() -> None:
    global _collection_ready
    if _collection_ready:
        return
    async with _collection_lock:
        if _collection_ready:
            return
        try:
            client = _get_client()
            exists = await client.collection_exists(settings.qdrant_collection)
            if not exists:
                await client.create_collection(
                    collection_name=settings.qdrant_collection,
                    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
                )
            _collection_ready = True
        except UnexpectedResponse as exc:
            if exc.status_code == 409:
                _collection_ready = True
                return
            logger.warning("Qdrant collection 초기화 실패: %s", exc)
        except Exception as exc:
            logger.warning("Qdrant collection 초기화 실패: %s", exc)


async def is_feedback_collection_ready() -> bool:
    await ensure_feedback_collection()
    return _collection_ready


async def upsert_feedback(
    feedback_id: int,
    vector: list[float],
    payload: dict[str, Any],
) -> None:
    await ensure_feedback_collection()
    if not _collection_ready:
        return
    try:
        await _get_client().upsert(
            collection_name=settings.qdrant_collection,
            points=[
                PointStruct(
                    id=feedback_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
    except Exception as exc:
        logger.warning("Qdrant feedback upsert 실패 feedback_id=%s: %s", feedback_id, exc)


async def search_similar(
    vector: list[float],
    style: str,
    gender: str | None,
    age_range: str | None,
    top_k: int | None = None,
) -> list[dict[str, Any]]:
    await ensure_feedback_collection()
    if not _collection_ready:
        return []

    conditions = [FieldCondition(key="style", match=MatchValue(value=style))]
    if gender is not None:
        conditions.append(FieldCondition(key="gender", match=MatchValue(value=gender)))
    if age_range is not None:
        conditions.append(FieldCondition(key="ageRange", match=MatchValue(value=age_range)))

    try:
        points = await _get_client().query_points(
            collection_name=settings.qdrant_collection,
            query=vector,
            query_filter=Filter(must=conditions),
            limit=top_k or settings.rag_top_k,
            with_payload=True,
        )
    except (UnexpectedResponse, Exception) as exc:
        logger.warning("Qdrant feedback 검색 실패: %s", exc)
        return []

    return [
        {
            "id": point.id,
            "score": point.score,
            "payload": point.payload or {},
        }
        for point in points.points
    ]
