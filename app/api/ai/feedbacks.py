from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.db.models import AvatarFeedback, AvatarFeedbackReason
from app.schemas.feedback import FeedbackIngestRequest, FeedbackIngestResponse

router = APIRouter()


@router.post("/feedbacks", response_model=FeedbackIngestResponse, status_code=201)
async def ingest_feedback(
    req: FeedbackIngestRequest,
    session: AsyncSession = Depends(get_session),
) -> FeedbackIngestResponse:
    feedback = AvatarFeedback(
        avatar_id=req.avatarId,
        job_id=req.jobId,
        rating=req.rating,
        comment=req.comment,
        training_consent=req.trainingConsent,
        feedback_use_consent=req.feedbackUseConsent,
        style=req.style,
        gender=req.gender,
        age_range=req.ageRange,
        prompt_version=req.promptVersion,
        model_name=req.modelName,
        reasons=[AvatarFeedbackReason(reason=r) for r in req.reasons],
    )
    session.add(feedback)
    await session.commit()
    return FeedbackIngestResponse(feedbackId=feedback.id)
