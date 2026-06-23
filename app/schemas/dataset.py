from __future__ import annotations

from pydantic import BaseModel

from app.schemas.feedback import FeedbackRating


class DatasetExportRequest(BaseModel):
    onlyTrainingConsented: bool = True
    minRating: FeedbackRating = FeedbackRating.LIKE
    promptVersion: str | None = None


class DatasetRow(BaseModel):
    input: dict
    output: dict
    metadata: dict


class DatasetExportResponse(BaseModel):
    exportJobId: str
    status: str
    trainUri: str
    evalUri: str
    manifestUri: str
    trainCount: int
    evalCount: int
