from __future__ import annotations

import logging
import time

from botocore.exceptions import ClientError
from google.genai.errors import APIError

from app.db.database import AsyncSessionLocal
from app.db.models import AvatarGenerationJob
from app.schemas.avatar import AvatarCallbackPayload, AvatarGenerationRequest, JobStatus
from app.services import callback, gemini_image, prompt, s3

logger = logging.getLogger(__name__)


async def process_avatar_job(job_id: str, req: AvatarGenerationRequest) -> None:
    async with AsyncSessionLocal() as session:
        job = await session.get(AvatarGenerationJob, job_id)
        if job is None:
            logger.error("job_id=%s 를 찾을 수 없음", job_id)
            return
        job.status = JobStatus.PROCESSING
        await session.commit()

    error_code: str | None = None
    error_message: str | None = None
    generated_uri: str | None = None
    prompt_text: str | None = None
    prompt_version: str | None = None
    status = JobStatus.COMPLETED
    start_time = time.monotonic()

    try:
        source_bytes = await s3.download_image(req.sourceImageUri)
        prompt_text, prompt_version = prompt.build_prompt(req.style, req.ageRange, req.gender)
        output_bytes = await gemini_image.generate_avatar_image(source_bytes, prompt_text)
        generated_uri = await s3.upload_image(output_bytes, req.avatarId)

    except ClientError as exc:
        logger.exception("S3 오류 job_id=%s", job_id)
        upload_started = generated_uri is None and prompt_text is not None
        error_code = "S3_UPLOAD_ERROR" if upload_started else "S3_DOWNLOAD_ERROR"
        error_message = str(exc)
        status = JobStatus.FAILED

    except APIError as exc:
        logger.exception("Gemini API 오류 job_id=%s", job_id)
        error_code = "GEMINI_API_ERROR"
        error_message = str(exc)
        status = JobStatus.FAILED

    except Exception as exc:
        logger.exception("알 수 없는 오류 job_id=%s", job_id)
        error_code = "INTERNAL_ERROR"
        error_message = str(exc)
        status = JobStatus.FAILED

    from app.core.config import settings

    duration_ms = int((time.monotonic() - start_time) * 1000)
    model_name = settings.gemini_image_model

    try:
        async with AsyncSessionLocal() as session:
            job = await session.get(AvatarGenerationJob, job_id)
            if job:
                job.status = status
                job.generated_image_uri = generated_uri
                job.model_name = model_name
                job.prompt_version = prompt_version
                job.prompt_text = prompt_text
                job.duration_ms = duration_ms
                job.error_code = error_code
                job.error_message = error_message
                await session.commit()
    except Exception as db_exc:
        logger.error("결과 저장 중 DB 오류 발생 job_id=%s: %s", job_id, db_exc)

    payload = AvatarCallbackPayload(
        avatarId=req.avatarId,
        jobId=job_id,
        status=status,
        generatedImageUri=generated_uri,
        modelName=model_name,
        promptVersion=prompt_version,
        promptText=prompt_text,
        durationMs=duration_ms,
        errorCode=error_code,
        errorMessage=error_message,
    )
    try:
        await callback.send_callback(req.callbackUrl, payload)
    except Exception as cb_exc:
        logger.error("콜백 전송 중 예외 발생 job_id=%s: %s", job_id, cb_exc)
