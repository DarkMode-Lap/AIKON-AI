from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.gemini import chat, chat_stream

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    reply = await chat(req.message)
    return ChatResponse(reply=reply)


@router.post("/stream")
async def chat_stream_endpoint(req: ChatRequest):
    return StreamingResponse(
        chat_stream(req.message),
        media_type="text/event-stream",
    )
