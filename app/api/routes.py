from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.services.ai_service import ai_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply = ai_service.process_message(request.message)
    return ChatResponse(reply=reply, status="success")