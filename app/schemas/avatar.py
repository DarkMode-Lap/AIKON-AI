from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class AvatarStyle(StrEnum):
    STUDIO = "STUDIO"
    ZOOTOPIA = "ZOOTOPIA"
    TRADITIONAL_HANBOK = "TRADITIONAL_HANBOK"
    DISNEY_PIXAR = "DISNEY_PIXAR"
    GHIBLI = "GHIBLI"
    LIGHT_ART = "LIGHT_ART"


class AvatarGender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class AvatarAgeRange(StrEnum):
    AGE_0_7 = "AGE_0_7"
    AGE_8_13 = "AGE_8_13"
    AGE_14_19 = "AGE_14_19"
    AGE_20_PLUS = "AGE_20_PLUS"


class JobStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AvatarGenerationRequest(BaseModel):
    avatarId: int
    sourceImageUri: str
    style: AvatarStyle
    gender: AvatarGender
    ageRange: AvatarAgeRange
    callbackUrl: str


class AvatarGenerationResponse(BaseModel):
    jobId: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jobId: str
    avatarId: int
    status: JobStatus
    generatedImageUri: str | None
    modelName: str | None
    errorCode: str | None
    ragEnabled: bool = False
    retrievedFeedbackIds: str | None = None
    retrievalQuery: str | None = None
    retrievalScores: str | None = None
    callbackStatus: str | None = None
    callbackError: str | None = None
    createdAt: datetime


class AvatarCallbackPayload(BaseModel):
    avatarId: int
    jobId: str
    status: JobStatus
    generatedImageUri: str | None
    modelName: str | None
    promptVersion: str | None
    promptText: str | None
    durationMs: int | None
    errorCode: str | None
    errorMessage: str | None
