from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import AvatarFeedback, AvatarGenerationJob
from app.schemas.dataset import DatasetExportRequest, DatasetExportResponse, DatasetRow
from app.schemas.feedback import FeedbackRating
from app.services.s3 import upload_text


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
    if req.minRating == FeedbackRating.LIKE:
        stmt = stmt.where(AvatarFeedback.rating == FeedbackRating.LIKE)
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

    export_job_id = f"dataset-export-{uuid4()}"
    created_at = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    base_key = f"datasets/avatar/{created_at}-{export_job_id}"
    train_uri = await upload_text(
        "\n".join(row.model_dump_json() for row in train_rows),
        f"{base_key}/train.jsonl",
        "application/x-ndjson",
    )
    eval_uri = await upload_text(
        "\n".join(row.model_dump_json() for row in eval_rows),
        f"{base_key}/eval.jsonl",
        "application/x-ndjson",
    )
    manifest = {
        "exportJobId": export_job_id,
        "createdAt": created_at,
        "onlyTrainingConsented": req.onlyTrainingConsented,
        "minRating": req.minRating,
        "promptVersion": req.promptVersion,
        "trainCount": len(train_rows),
        "evalCount": len(eval_rows),
        "trainUri": train_uri,
        "evalUri": eval_uri,
    }
    manifest_uri = await upload_text(
        json.dumps(manifest, ensure_ascii=False),
        f"{base_key}/manifest.json",
    )

    return DatasetExportResponse(
        exportJobId=export_job_id,
        status="COMPLETED",
        trainUri=train_uri,
        evalUri=eval_uri,
        manifestUri=manifest_uri,
        trainCount=len(train_rows),
        evalCount=len(eval_rows),
    )
