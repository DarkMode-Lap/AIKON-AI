from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.schemas.dataset import DatasetExportRequest, DatasetExportResponse
from app.services.dataset_export import export_dataset

router = APIRouter()


@router.post("/datasets/exports", response_model=DatasetExportResponse)
async def create_dataset_export(
    req: DatasetExportRequest,
    session: AsyncSession = Depends(get_session),
) -> DatasetExportResponse:
    return await export_dataset(req, session)
