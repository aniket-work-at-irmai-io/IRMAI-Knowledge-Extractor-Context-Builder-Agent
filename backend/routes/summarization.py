from fastapi import APIRouter, HTTPException
from models.api_models import TextInput, ModelTypeInput
from services.summarization_service import SummarizationService

router = APIRouter(prefix="/api/summarization", tags=["summarization"])

@router.post("/summarize")
async def summarize_text(request: TextInput, model_type: ModelTypeInput):
    try:
        summary = SummarizationService.summarize_text(request.text, model_type.model_type)
        return {"status": "success", "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing text: {str(e)}")