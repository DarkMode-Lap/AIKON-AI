from fastapi import APIRouter

from app.api.ai.avatar_generations import router as avatar_router
from app.api.ai.datasets import router as datasets_router
from app.api.ai.feedbacks import router as feedbacks_router

router = APIRouter()
router.include_router(avatar_router)
router.include_router(feedbacks_router)
router.include_router(datasets_router)
