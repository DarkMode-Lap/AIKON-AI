from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AvatarFeedback, AvatarGenerationJob
from app.schemas.dataset import DatasetExportRequest, DatasetExportResponse, DatasetRow
from app.schemas.feedback import FeedbackRating


async def export_dataset(
    req: DatasetExportRequest,
    session: AsyncSession,
) -> DatasetExportResponse:
    stmt = select(AvatarFeedback)
    if req.onlyTrainingConsented:
        stmt = stmt.where(AvatarFeedback.training_consent.is_(True))
    if req.promptVersion:
        stmt = stmt.where(AvatarFeedback.prompt_version == req.promptVersion)

    result = await session.execute(stmt)
    feedbacks = result.scalars().all()

    job_ids = list({f.job_id for f in feedbacks if f.job_id})
    jobs_by_id: dict[str, AvatarGenerationJob] = {}
    if job_ids:
        job_result = await session.execute(
            select(AvatarGenerationJob).where(AvatarGenerationJob.id.in_(job_ids))
        )
        jobs_by_id = {j.id: j for j in job_result.scalars().all()}

    train_rows: list[DatasetRow] = []
    eval_rows: list[DatasetRow] = []

    for f in feedbacks:
        job = jobs_by_id.get(f.job_id) if f.job_id else None
        try:
            reasons = json.loads(f.reasons)
            if not isinstance(reasons, list):
                reasons = []
        except (json.JSONDecodeError, TypeError):
            reasons = []
        row = DatasetRow(
            input={
                "prompt": job.prompt_text if job else None,
                "sourceImageUri": job.source_image_uri if job else None,
                "style": f.style,
                "gender": f.gender,
                "ageRange": f.age_range,
            },
            output={
                "imageUri": job.generated_image_uri if job else None,
            },
            metadata={
                "rating": f.rating,
                "reasons": reasons,
                "promptVersion": f.prompt_version,
                "modelName": f.model_name,
            },
        )
        if f.rating == FeedbackRating.LIKE:
            train_rows.append(row)
        else:
            eval_rows.append(row)

    return DatasetExportResponse(
        trainCount=len(train_rows),
        evalCount=len(eval_rows),
        trainData=train_rows,
        evalData=eval_rows,
    )
