# backend/routes/guidelines.py
from fastapi import APIRouter, HTTPException
from services.guidelines_service import GuidelinesService

router = APIRouter(prefix="/api/guidelines", tags=["guidelines"])

@router.post("/generate")
async def generate_guidelines():
    try:
        result = GuidelinesService.generate_guidelines()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating guidelines: {str(e)}")