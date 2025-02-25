from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any

class URLInput(BaseModel):
    url: HttpUrl

class TextInput(BaseModel):
    text: str

class ModelTypeInput(BaseModel):
    model_type: str

class QuestionInput(BaseModel):
    question: str
    model_type: str

class ChatHistoryItem(BaseModel):
    user: str
    bot: str

class ChatHistory(BaseModel):
    history: List[ChatHistoryItem]