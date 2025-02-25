import os
import sys
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import nest_asyncio

# Set Windows event loop policy
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

load_dotenv()
nest_asyncio.apply()

# Import routes
from routes import extraction, summarization, embeddings, chat
from utils.config_utils import CONFIG

# Create FastAPI app
app = FastAPI(title="IRMAI Knowledge Extractor & Context Builder Agent API", description="API for IRMAI Knowledge Extractor & Context Builder Agent RAG Chatbot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(extraction.router)
app.include_router(summarization.router)
app.include_router(embeddings.router)
app.include_router(chat.router)

if __name__ == "__main__":
    host = CONFIG["server"]["host"]
    port = CONFIG["server"]["port"]
    debug = CONFIG["server"]["debug"]
    uvicorn.run(app, host=host, port=port)