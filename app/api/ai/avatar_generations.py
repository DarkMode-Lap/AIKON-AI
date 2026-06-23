import json
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.db.models import AvatarGenerationJob
from app.schemas.avatar import (
    AvatarGenerationRequest,
    AvatarGenerationResponse,
    JobStatus,
    JobStatusResponse,
)
from app.services.avatar_job_processor import process_avatar_job

router = APIRouter()


@router.post("/avatar-generations", response_model=AvatarGenerationResponse, status_code=202)
async def create_avatar_generation(
    req: AvatarGenerationRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> AvatarGenerationResponse:
    job_id = str(uuid4())
    job = AvatarGenerationJob(
        id=job_id,
        avatar_id=req.avatarId,
        status=JobStatus.ACCEPTED,
        style=req.style,
        gender=req.gender,
        age_range=req.ageRange,
        source_image_uri=req.sourceImageUri,
        callback_url=req.callbackUrl,
    )
    session.add(job)
    await session.commit()
    background_tasks.add_task(process_avatar_job, job_id, req)
    return AvatarGenerationResponse(jobId=job_id, status=JobStatus.ACCEPTED)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> JobStatusResponse:
    job = await session.get(AvatarGenerationJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job을 찾을 수 없습니다")
    return JobStatusResponse(
        jobId=job.id,
        avatarId=job.avatar_id,
        status=job.status,
        generatedImageUri=job.generated_image_uri,
        modelName=job.model_name,
        errorCode=job.error_code,
        ragEnabled=job.rag_enabled,
        retrievedFeedbackIds=json.loads(job.retrieved_feedback_ids)
        if job.retrieved_feedback_ids
        else None,
        retrievalQuery=job.retrieval_query,
        retrievalScores=json.loads(job.retrieval_scores) if job.retrieval_scores else None,
        callbackStatus=job.callback_status,
        callbackError=job.callback_error,
        createdAt=job.created_at,
    )
