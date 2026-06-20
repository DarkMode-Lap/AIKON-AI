from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel

from app.schemas.avatar import AvatarAgeRange, AvatarGender, AvatarStyle


class FeedbackRating(StrEnum):
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"


class FeedbackReason(StrEnum):
    FACE_SIMILARITY = "FACE_SIMILARITY"
    STYLE_MATCH = "STYLE_MATCH"
    BACKGROUND = "BACKGROUND"
    DETAIL_BROKEN = "DETAIL_BROKEN"
    AGE_MISMATCH = "AGE_MISMATCH"
    TOO_DIFFERENT = "TOO_DIFFERENT"
    GOOD_QUALITY = "GOOD_QUALITY"
    BAD_QUALITY = "BAD_QUALITY"


class FeedbackIngestRequest(BaseModel):
    avatarId: int
    jobId: str | None = None
    rating: FeedbackRating
    reasons: list[FeedbackReason]
    comment: str | None = None
    trainingConsent: bool
    feedbackUseConsent: bool
    style: AvatarStyle
    gender: AvatarGender
    ageRange: AvatarAgeRange
    promptVersion: str | None = None
    modelName: str | None = None


class FeedbackIngestResponse(BaseModel):
    feedbackId: int
