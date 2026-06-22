from __future__ import annotations

import logging
from typing import Any

from app.db.vector_store import is_feedback_collection_ready, upsert_feedback
from app.services.embedding import embed_text

logger = logging.getLogger(__name__)


def build_rag_document(feedback: dict[str, Any]) -> str:
    reasons = ",".join(feedback["reasons"])
    comment = feedback.get("comment") or ""
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
    if not feedback["feedbackUseConsent"]:
        return
    if not feedback["reasons"]:
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
                "comment": feedback.get("comment"),
                "promptVersion": feedback.get("promptVersion"),
                "modelName": feedback.get("modelName"),
            },
        )
    except Exception as exc:
        logger.warning("Feedback RAG 처리 실패 feedback_id=%s: %s", feedback.get("feedbackId"), exc)
