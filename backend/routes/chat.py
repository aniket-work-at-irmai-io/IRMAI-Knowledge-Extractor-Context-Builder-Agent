from fastapi import APIRouter, HTTPException
from models.api_models import QuestionInput, ChatHistory
from services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/ask")
async def ask_question(request: QuestionInput, chat_history: ChatHistory = None):
    try:
        history = None if chat_history is None else [item.dict() for item in chat_history.history]
        result = ChatService.ask_question(request.question, request.model_type, history)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error asking question: {str(e)}")