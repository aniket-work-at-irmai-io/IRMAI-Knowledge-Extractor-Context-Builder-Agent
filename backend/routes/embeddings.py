from fastapi import APIRouter, HTTPException
from models.api_models import TextInput
from services.embeddings_service import EmbeddingsService

router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])

@router.post("/create")
async def create_embeddings(request: TextInput):
    try:
        result = EmbeddingsService.create_embeddings(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating embeddings: {str(e)}")