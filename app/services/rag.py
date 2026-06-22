from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.db.vector_store import is_feedback_collection_ready, search_similar
from app.schemas.avatar import AvatarAgeRange, AvatarGender, AvatarStyle
from app.services.embedding import embed_text


@dataclass(frozen=True)
class RagContextResult:
    context: str
    retrieved_feedback_ids: list[int]


async def retrieve_rag_context(
    style: AvatarStyle,
    gender: AvatarGender,
    age_range: AvatarAgeRange,
) -> RagContextResult:
    try:
        if not await is_feedback_collection_ready():
            return RagContextResult(context="", retrieved_feedback_ids=[])
        query_text = f"style={style.value} gender={gender.value} ageRange={age_range.value}"
        vector = await embed_text(query_text)
        results = await search_similar(
            vector,
            style=style.value,
            gender=gender.value,
            age_range=age_range.value,
        )
        if not results:
            results = await search_similar(
                vector,
                style=style.value,
                gender=None,
                age_range=None,
            )
    except Exception:
        return RagContextResult(context="", retrieved_feedback_ids=[])

    context = build_rag_context(results)
    feedback_ids = [
        int(result["payload"]["feedbackId"])
        for result in results
        if result.get("payload", {}).get("feedbackId") is not None
    ]
    return RagContextResult(context=context, retrieved_feedback_ids=feedback_ids)


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
