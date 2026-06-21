from fastapi import APIRouter

from app.api.admin.metrics import router as metrics_router

router = APIRouter()
router.include_router(metrics_router, prefix="/metrics", tags=["admin"])
