from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.core.config import settings
from app.db.vector_store import is_feedback_collection_ready, search_similar
from app.schemas.avatar import AvatarAgeRange, AvatarGender, AvatarStyle
from app.services.embedding import embed_text

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RagContextResult:
    context: str
    retrieved_feedback_ids: list[int]
    retrieval_query: str = ""
    retrieval_scores: list[float] | None = None


async def retrieve_rag_context(
    style: AvatarStyle,
    gender: AvatarGender | None,
    age_range: AvatarAgeRange | None,
) -> RagContextResult:
    try:
        if not await is_feedback_collection_ready():
            return RagContextResult(context="", retrieved_feedback_ids=[])
        gender_value = gender.value if gender is not None else None
        age_range_value = age_range.value if age_range is not None else None
        query_gender = gender_value or "UNKNOWN"
        query_age_range = age_range_value or "UNKNOWN"
        query_text = f"style={style.value} gender={query_gender} ageRange={query_age_range}"
        vector = await embed_text(query_text)
        results = await search_similar(
            vector,
            style=style.value,
            gender=gender_value,
            age_range=age_range_value,
        )
        if not results and (gender_value is not None or age_range_value is not None):
            results = await search_similar(
                vector,
                style=style.value,
                gender=None,
                age_range=None,
            )
    except Exception as exc:
        logger.warning("RAG 컨텍스트 조회 실패: %s", exc)
        return RagContextResult(context="", retrieved_feedback_ids=[])

    results = [
        result for result in results if float(result.get("score") or 0.0) >= settings.rag_min_score
    ]
    context = build_rag_context(results)
    feedback_ids = [
        int(result["payload"]["feedbackId"])
        for result in results
        if result.get("payload", {}).get("feedbackId") is not None
    ]
    scores = [float(result.get("score") or 0.0) for result in results]
    return RagContextResult(
        context=context,
        retrieved_feedback_ids=feedback_ids,
        retrieval_query=query_text,
        retrieval_scores=scores,
    )


def build_rag_context(results: list[dict[str, Any]]) -> str:
    if not results:
        return ""

    positive = [
        _format_feedback(result["payload"]) for result in results if _rating(result) == "LIKE"
    ]
    negative = [
        _format_feedback(result["payload"]) for result in results if _rating(result) == "DISLIKE"
    ]

    lines = [
        "Use the following prior avatar feedback as guidance.",
    ]
    if positive:
        lines.append("Positive feedback patterns to preserve:")
        lines.extend(f"- {item}" for item in positive)
    if negative:
        lines.append("Negative feedback patterns to avoid:")
        lines.extend(f"- {item}" for item in negative)
    return "\n".join(lines)


def _rating(result: dict[str, Any]) -> str:
    return str(result.get("payload", {}).get("rating", ""))


def _format_feedback(payload: dict[str, Any]) -> str:
    reasons = payload.get("reasons") or []
    guidance = [_reason_to_english(str(reason)) for reason in reasons]
    guidance = [item for item in guidance if item]
    if guidance:
        return "; ".join(guidance)
    return "No specific reason labels were provided."


def _reason_to_english(reason: str) -> str:
    reason_map = {
        "FACE_SIMILARITY": "Preserve stronger facial similarity from the source image.",
        "STYLE_MATCH": "Keep the requested visual style consistent.",
        "BACKGROUND": "Keep the background clean and aligned with the style.",
        "DETAIL_BROKEN": "Avoid broken facial details, artifacts, or distorted features.",
        "AGE_MISMATCH": "Match the requested age range more accurately.",
        "TOO_DIFFERENT": "Avoid changing the person's identity too much.",
        "GOOD_QUALITY": "Preserve clean details and high visual quality.",
        "BAD_QUALITY": "Avoid low-quality rendering, blur, or messy details.",
    }
    return reason_map.get(reason, "")
