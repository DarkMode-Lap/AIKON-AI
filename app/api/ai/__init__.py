from fastapi import APIRouter

from app.api.ai.avatar_generations import router as avatar_router

router = APIRouter()
router.include_router(avatar_router)
