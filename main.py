from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.ai import router as ai_router
from app.api.v1 import router as v1_router
from app.core.config import settings
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.include_router(v1_router, prefix="/api")
app.include_router(ai_router, prefix="/ai")


@app.get("/health")
async def health():
    return {"status": "ok"}
