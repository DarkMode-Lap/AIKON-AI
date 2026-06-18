from fastapi import FastAPI

from app.api.v1 import router as v1_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(v1_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
