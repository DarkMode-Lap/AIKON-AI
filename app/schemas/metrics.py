from __future__ import annotations

from pydantic import BaseModel


class StyleStat(BaseModel):
    count: int
    successRate: float


class PromptVersionStat(BaseModel):
    count: int
    successRate: float


class GenerationMetrics(BaseModel):
    totalCount: int
    completedCount: int
    failedCount: int
    successRate: float
    avgDurationMs: float | None
    byStyle: dict[str, StyleStat]
    byPromptVersion: dict[str, PromptVersionStat]


class StyleFeedbackStat(BaseModel):
    likeCount: int
    dislikeCount: int
    likeRate: float


class PromptVersionFeedbackStat(BaseModel):
    likeCount: int
    dislikeCount: int
    likeRate: float


class FeedbackMetrics(BaseModel):
    totalCount: int
    likeCount: int
    dislikeCount: int
    likeRate: float
    byReason: dict[str, int]
    byStyle: dict[str, StyleFeedbackStat]
    byPromptVersion: dict[str, PromptVersionFeedbackStat]
    trainingConsentCount: int
    feedbackUseConsentCount: int
