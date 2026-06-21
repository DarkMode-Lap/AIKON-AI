from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import AvatarFeedback, AvatarGenerationJob
from app.schemas.dataset import DatasetExportRequest, DatasetExportResponse, DatasetRow
from app.schemas.feedback import FeedbackRating


async def export_dataset(
    req: DatasetExportRequest,
    session: AsyncSession,
) -> DatasetExportResponse:
    stmt = (
        select(AvatarFeedback, AvatarGenerationJob)
        .outerjoin(AvatarGenerationJob, AvatarFeedback.job_id == AvatarGenerationJob.id)
        .options(selectinload(AvatarFeedback.reasons))
    )
    if req.onlyTrainingConsented:
        stmt = stmt.where(AvatarFeedback.training_consent.is_(True))
    if req.promptVersion:
        stmt = stmt.where(AvatarFeedback.prompt_version == req.promptVersion)

    result = await session.execute(stmt)
    feedbacks_with_jobs = result.all()

    train_rows: list[DatasetRow] = []
    eval_rows: list[DatasetRow] = []

    for f, job in feedbacks_with_jobs:
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
                "reasons": [r.reason for r in f.reasons],
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
