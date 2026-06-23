from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.db.models import AvatarFeedback, AvatarFeedbackReason, AvatarGenerationJob
from app.schemas.metrics import (
    FeedbackMetrics,
    GenerationMetrics,
    PromptVersionFeedbackStat,
    PromptVersionStat,
    RagImpactMetrics,
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
    since = datetime.now(UTC) - timedelta(days=days)

    def _base_where(stmt):
        stmt = stmt.where(AvatarGenerationJob.created_at >= since)
        if style:
            stmt = stmt.where(AvatarGenerationJob.style == style)
        if prompt_version:
            stmt = stmt.where(AvatarGenerationJob.prompt_version == prompt_version)
        return stmt

    total_stmt = _base_where(
        select(
            func.count(AvatarGenerationJob.id).label("total"),
            func.sum(case((AvatarGenerationJob.status == "COMPLETED", 1), else_=0)).label(
                "completed"
            ),
            func.sum(case((AvatarGenerationJob.status == "FAILED", 1), else_=0)).label("failed"),
            func.avg(AvatarGenerationJob.duration_ms).label("avg_duration"),
        )
    )
    row = (await session.execute(total_stmt)).one()
    total = row.total or 0
    completed = row.completed or 0
    failed = row.failed or 0
    avg_duration = float(row.avg_duration) if row.avg_duration is not None else None

    style_stmt = _base_where(
        select(
            AvatarGenerationJob.style,
            func.count(AvatarGenerationJob.id).label("count"),
            func.sum(case((AvatarGenerationJob.status == "COMPLETED", 1), else_=0)).label(
                "completed"
            ),
        ).group_by(AvatarGenerationJob.style)
    )
    by_style = {
        r.style: StyleStat(
            count=r.count,
            successRate=r.completed / r.count if r.count else 0.0,
        )
        for r in (await session.execute(style_stmt)).all()
    }

    version_stmt = _base_where(
        select(
            func.coalesce(AvatarGenerationJob.prompt_version, "unknown").label("version"),
            func.count(AvatarGenerationJob.id).label("count"),
            func.sum(case((AvatarGenerationJob.status == "COMPLETED", 1), else_=0)).label(
                "completed"
            ),
        ).group_by(func.coalesce(AvatarGenerationJob.prompt_version, "unknown"))
    )
    by_prompt = {
        r.version: PromptVersionStat(
            count=r.count,
            successRate=r.completed / r.count if r.count else 0.0,
        )
        for r in (await session.execute(version_stmt)).all()
    }

    return GenerationMetrics(
        totalCount=total,
        completedCount=completed,
        failedCount=failed,
        successRate=completed / total if total else 0.0,
        avgDurationMs=avg_duration,
        byStyle=by_style,
        byPromptVersion=by_prompt,
    )


@router.get("/feedbacks", response_model=FeedbackMetrics)
async def get_feedback_metrics(
    style: str | None = Query(default=None),
    prompt_version: str | None = Query(default=None),
    days: int = Query(default=30, ge=1),
    session: AsyncSession = Depends(get_session),
) -> FeedbackMetrics:
    since = datetime.now(UTC) - timedelta(days=days)

    def _base_where(stmt):
        stmt = stmt.where(AvatarFeedback.created_at >= since)
        if style:
            stmt = stmt.where(AvatarFeedback.style == style)
        if prompt_version:
            stmt = stmt.where(AvatarFeedback.prompt_version == prompt_version)
        return stmt

    total_stmt = _base_where(
        select(
            func.count(AvatarFeedback.id).label("total"),
            func.sum(case((AvatarFeedback.rating == "LIKE", 1), else_=0)).label("likes"),
            func.sum(case((AvatarFeedback.training_consent.is_(True), 1), else_=0)).label(
                "training_consent"
            ),
            func.sum(case((AvatarFeedback.feedback_use_consent.is_(True), 1), else_=0)).label(
                "feedback_use"
            ),
        )
    )
    row = (await session.execute(total_stmt)).one()
    total = row.total or 0
    likes = row.likes or 0
    dislikes = total - likes

    style_stmt = _base_where(
        select(
            AvatarFeedback.style,
            func.sum(case((AvatarFeedback.rating == "LIKE", 1), else_=0)).label("likes"),
            func.sum(case((AvatarFeedback.rating == "DISLIKE", 1), else_=0)).label("dislikes"),
        ).group_by(AvatarFeedback.style)
    )
    by_style = {
        r.style: StyleFeedbackStat(
            likeCount=r.likes or 0,
            dislikeCount=r.dislikes or 0,
            likeRate=(r.likes or 0) / ((r.likes or 0) + (r.dislikes or 0))
            if (r.likes or 0) + (r.dislikes or 0)
            else 0.0,
        )
        for r in (await session.execute(style_stmt)).all()
    }

    version_stmt = _base_where(
        select(
            func.coalesce(AvatarFeedback.prompt_version, "unknown").label("version"),
            func.sum(case((AvatarFeedback.rating == "LIKE", 1), else_=0)).label("likes"),
            func.sum(case((AvatarFeedback.rating == "DISLIKE", 1), else_=0)).label("dislikes"),
        ).group_by(func.coalesce(AvatarFeedback.prompt_version, "unknown"))
    )
    by_prompt = {
        r.version: PromptVersionFeedbackStat(
            likeCount=r.likes or 0,
            dislikeCount=r.dislikes or 0,
            likeRate=(r.likes or 0) / ((r.likes or 0) + (r.dislikes or 0))
            if (r.likes or 0) + (r.dislikes or 0)
            else 0.0,
        )
        for r in (await session.execute(version_stmt)).all()
    }

    reasons_stmt = _base_where(
        select(
            AvatarFeedbackReason.reason,
            func.count(AvatarFeedbackReason.id).label("cnt"),
        )
        .join(AvatarFeedbackReason, AvatarFeedback.id == AvatarFeedbackReason.feedback_id)
        .group_by(AvatarFeedbackReason.reason)
    )
    reason_counts: dict[str, int] = {
        r.reason: r.cnt for r in (await session.execute(reasons_stmt)).all()
    }

    return FeedbackMetrics(
        totalCount=total,
        likeCount=likes,
        dislikeCount=dislikes,
        likeRate=likes / total if total else 0.0,
        byReason=reason_counts,
        byStyle=by_style,
        byPromptVersion=by_prompt,
        trainingConsentCount=row.training_consent or 0,
        feedbackUseConsentCount=row.feedback_use or 0,
    )


@router.get("/rag-impact", response_model=RagImpactMetrics)
async def get_rag_impact_metrics(
    style: str | None = Query(default=None),
    prompt_version: str | None = Query(default=None),
    days: int = Query(default=30, ge=1),
    session: AsyncSession = Depends(get_session),
) -> RagImpactMetrics:
    since = datetime.now(UTC) - timedelta(days=days)

    def _base_where(stmt):
        stmt = stmt.where(AvatarGenerationJob.created_at >= since)
        if style:
            stmt = stmt.where(AvatarGenerationJob.style == style)
        if prompt_version:
            stmt = stmt.where(AvatarGenerationJob.prompt_version == prompt_version)
        return stmt

    total_stmt = _base_where(
        select(
            func.count(AvatarGenerationJob.id).label("total"),
            func.sum(case((AvatarGenerationJob.rag_enabled.is_(True), 1), else_=0)).label(
                "rag_enabled"
            ),
        )
    )
    row = (await session.execute(total_stmt)).one()
    total = row.total or 0
    rag_enabled = row.rag_enabled or 0

    feedback_join = AvatarFeedback.job_id == AvatarGenerationJob.id
    like_stmt = _base_where(
        select(
            func.sum(
                case(
                    (
                        (AvatarGenerationJob.rag_enabled.is_(True))
                        & (AvatarFeedback.rating == "LIKE"),
                        1,
                    ),
                    else_=0,
                )
            ).label("rag_likes"),
            func.sum(
                case(
                    (
                        (AvatarGenerationJob.rag_enabled.is_(True))
                        & (AvatarFeedback.id.is_not(None)),
                        1,
                    ),
                    else_=0,
                )
            ).label("rag_feedbacks"),
            func.sum(
                case(
                    (
                        (AvatarGenerationJob.rag_enabled.is_(False))
                        & (AvatarFeedback.rating == "LIKE"),
                        1,
                    ),
                    else_=0,
                )
            ).label("non_rag_likes"),
            func.sum(
                case(
                    (
                        (AvatarGenerationJob.rag_enabled.is_(False))
                        & (AvatarFeedback.id.is_not(None)),
                        1,
                    ),
                    else_=0,
                )
            ).label("non_rag_feedbacks"),
        ).outerjoin(AvatarFeedback, feedback_join)
    )
    like_row = (await session.execute(like_stmt)).one()
    rag_feedbacks = like_row.rag_feedbacks or 0
    non_rag_feedbacks = like_row.non_rag_feedbacks or 0

    score_stmt = _base_where(
        select(AvatarGenerationJob.retrieval_scores).where(
            AvatarGenerationJob.retrieval_scores.is_not(None)
        )
    )
    scores: list[float] = []
    result = await session.stream_scalars(score_stmt)
    async for retrieval_scores in result:
        try:
            scores.extend(float(value) for value in json.loads(retrieval_scores))
        except (TypeError, ValueError, json.JSONDecodeError):
            continue

    return RagImpactMetrics(
        totalCount=total,
        ragEnabledCount=rag_enabled,
        ragDisabledCount=total - rag_enabled,
        ragHitRate=rag_enabled / total if total else 0.0,
        ragLikeRate=(like_row.rag_likes or 0) / rag_feedbacks if rag_feedbacks else 0.0,
        nonRagLikeRate=(like_row.non_rag_likes or 0) / non_rag_feedbacks
        if non_rag_feedbacks
        else 0.0,
        avgRetrievalScore=sum(scores) / len(scores) if scores else None,
    )
