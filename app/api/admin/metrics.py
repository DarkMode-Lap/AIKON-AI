from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.db.models import AvatarFeedback, AvatarGenerationJob
from app.schemas.metrics import (
    FeedbackMetrics,
    GenerationMetrics,
    PromptVersionFeedbackStat,
    PromptVersionStat,
    StyleFeedbackStat,
    StyleStat,
)

router = APIRouter()


@router.get("/generations", response_model=GenerationMetrics)
async def get_generation_metrics(
    style: str | None = Query(default=None),
    prompt_version: str | None = Query(default=None),
    days: int = Query(default=30, ge=1),
    session: AsyncSession = Depends(get_session),
) -> GenerationMetrics:
    since = datetime.utcnow() - timedelta(days=days)

    stmt = select(AvatarGenerationJob).where(AvatarGenerationJob.created_at >= since)
    if style:
        stmt = stmt.where(AvatarGenerationJob.style == style)
    if prompt_version:
        stmt = stmt.where(AvatarGenerationJob.prompt_version == prompt_version)

    result = await session.execute(stmt)
    jobs = result.scalars().all()

    total = len(jobs)
    completed = sum(1 for j in jobs if j.status == "COMPLETED")
    failed = sum(1 for j in jobs if j.status == "FAILED")
    success_rate = completed / total if total else 0.0

    durations = [j.duration_ms for j in jobs if j.duration_ms is not None]
    avg_duration = sum(durations) / len(durations) if durations else None

    by_style: dict[str, dict] = defaultdict(lambda: {"count": 0, "completed": 0})
    for j in jobs:
        by_style[j.style]["count"] += 1
        if j.status == "COMPLETED":
            by_style[j.style]["completed"] += 1

    by_prompt: dict[str, dict] = defaultdict(lambda: {"count": 0, "completed": 0})
    for j in jobs:
        key = j.prompt_version or "unknown"
        by_prompt[key]["count"] += 1
        if j.status == "COMPLETED":
            by_prompt[key]["completed"] += 1

    return GenerationMetrics(
        totalCount=total,
        completedCount=completed,
        failedCount=failed,
        successRate=success_rate,
        avgDurationMs=avg_duration,
        byStyle={
            k: StyleStat(
                count=v["count"],
                successRate=v["completed"] / v["count"] if v["count"] else 0.0,
            )
            for k, v in by_style.items()
        },
        byPromptVersion={
            k: PromptVersionStat(
                count=v["count"],
                successRate=v["completed"] / v["count"] if v["count"] else 0.0,
            )
            for k, v in by_prompt.items()
        },
    )


@router.get("/feedbacks", response_model=FeedbackMetrics)
async def get_feedback_metrics(
    style: str | None = Query(default=None),
    prompt_version: str | None = Query(default=None),
    days: int = Query(default=30, ge=1),
    session: AsyncSession = Depends(get_session),
) -> FeedbackMetrics:
    since = datetime.utcnow() - timedelta(days=days)

    stmt = select(AvatarFeedback).where(AvatarFeedback.created_at >= since)
    if style:
        stmt = stmt.where(AvatarFeedback.style == style)
    if prompt_version:
        stmt = stmt.where(AvatarFeedback.prompt_version == prompt_version)

    result = await session.execute(stmt)
    feedbacks = result.scalars().all()

    total = len(feedbacks)
    likes = sum(1 for f in feedbacks if f.rating == "LIKE")
    dislikes = total - likes
    like_rate = likes / total if total else 0.0

    reason_counts: dict[str, int] = defaultdict(int)
    for f in feedbacks:
        for reason in json.loads(f.reasons):
            reason_counts[reason] += 1

    by_style: dict[str, dict] = defaultdict(lambda: {"like": 0, "dislike": 0})
    for f in feedbacks:
        if f.rating == "LIKE":
            by_style[f.style]["like"] += 1
        else:
            by_style[f.style]["dislike"] += 1

    by_prompt: dict[str, dict] = defaultdict(lambda: {"like": 0, "dislike": 0})
    for f in feedbacks:
        key = f.prompt_version or "unknown"
        if f.rating == "LIKE":
            by_prompt[key]["like"] += 1
        else:
            by_prompt[key]["dislike"] += 1

    def _feedback_stat(v: dict) -> StyleFeedbackStat:
        total_v = v["like"] + v["dislike"]
        return StyleFeedbackStat(
            likeCount=v["like"],
            dislikeCount=v["dislike"],
            likeRate=v["like"] / total_v if total_v else 0.0,
        )

    return FeedbackMetrics(
        totalCount=total,
        likeCount=likes,
        dislikeCount=dislikes,
        likeRate=like_rate,
        byReason=dict(reason_counts),
        byStyle={k: _feedback_stat(v) for k, v in by_style.items()},
        byPromptVersion={
            k: PromptVersionFeedbackStat(
                likeCount=v["like"],
                dislikeCount=v["dislike"],
                likeRate=v["like"] / (v["like"] + v["dislike"])
                if (v["like"] + v["dislike"])
                else 0.0,
            )
            for k, v in by_prompt.items()
        },
        trainingConsentCount=sum(1 for f in feedbacks if f.training_consent),
        feedbackUseConsentCount=sum(1 for f in feedbacks if f.feedback_use_consent),
    )
