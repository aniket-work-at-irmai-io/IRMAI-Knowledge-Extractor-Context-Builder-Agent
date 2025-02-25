from fastapi import APIRouter, HTTPException
import asyncio
from models.api_models import URLInput, TextInput
from services.extraction_service import ExtractionService

router = APIRouter(prefix="/api/extraction", tags=["extraction"])

@router.post("/extract")
async def extract_website(url_input: URLInput):
    try:
        extracted_text = await ExtractionService.extract_website(str(url_input.url))
        return {"status": "success", "text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting website: {str(e)}")