from __future__ import annotations

import logging
import re
from typing import Any

from app.db.vector_store import is_feedback_collection_ready, upsert_feedback
from app.services.embedding import embed_text

logger = logging.getLogger(__name__)

MIN_COMMENT_LENGTH = 8
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_PHONE_RE = re.compile(r"\b(?:\+?\d[\d -]{7,}\d)\b")
_URL_RE = re.compile(r"https?://\S+|s3://\S+|gs://\S+")
_PATH_RE = re.compile(r"(?:/[A-Za-z0-9_. -]+){2,}")


def sanitize_feedback_comment(comment: str | None) -> str:
    if not comment:
        return ""
    sanitized = _EMAIL_RE.sub("[email]", comment)
    sanitized = _PHONE_RE.sub("[phone]", sanitized)
    sanitized = _URL_RE.sub("[uri]", sanitized)
    sanitized = _PATH_RE.sub("[path]", sanitized)
    return " ".join(sanitized.split())


def is_useful_feedback(feedback: dict[str, Any]) -> bool:
    if not feedback.get("feedbackUseConsent"):
        return False
    if not feedback.get("reasons"):
        return False
    comment = sanitize_feedback_comment(feedback.get("comment"))
    if feedback.get("rating") == "DISLIKE" and len(comment) < MIN_COMMENT_LENGTH:
        return False
    return True


def build_rag_document(feedback: dict[str, Any]) -> str:
    reasons = ",".join(feedback["reasons"])
    comment = sanitize_feedback_comment(feedback.get("comment"))
    return "\n".join(
        [
            (
                f"style={feedback['style']} gender={feedback['gender']} "
                f"ageRange={feedback['ageRange']}"
            ),
            f"rating={feedback['rating']} reasons={reasons}",
            f"feedback: {comment}",
        ]
    )


async def process_feedback_for_rag(feedback: dict[str, Any]) -> None:
    if not is_useful_feedback(feedback):
        return

    try:
        if not await is_feedback_collection_ready():
            return
        document = build_rag_document(feedback)
        vector = await embed_text(document)
        await upsert_feedback(
            feedback_id=feedback["feedbackId"],
            vector=vector,
            payload={
                "feedbackId": feedback["feedbackId"],
                "style": feedback["style"],
                "gender": feedback["gender"],
                "ageRange": feedback["ageRange"],
                "rating": feedback["rating"],
                "reasons": feedback["reasons"],
                "comment": sanitize_feedback_comment(feedback.get("comment")),
                "promptVersion": feedback.get("promptVersion"),
                "modelName": feedback.get("modelName"),
            },
        )
    except Exception as exc:
        logger.warning("Feedback RAG 처리 실패 feedback_id=%s: %s", feedback.get("feedbackId"), exc)
