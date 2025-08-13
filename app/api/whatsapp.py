from fastapi import APIRouter
from app.schemas.whatsapp import ChatRequest, ChatResponse
from app.agents.whatsapp_handler import whatsapp_chat

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    response = await whatsapp_chat(request.user_id, request.user_input)
    return ChatResponse(status="success", response=response)
