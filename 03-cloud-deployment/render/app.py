"""
AI Agent ready for Render deployment.
Render tự động inject PORT env var — app phải đọc từ os.getenv("PORT").
"""
import os
import time
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from utils.mock_llm import ask

app = FastAPI(
    title="AI Agent on Render",
    version="1.0.0",
    description="Production-ready AI agent deployed on Render"
)

START_TIME = time.time()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production, chỉ định domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint với thông tin cơ bản"""
    return {
        "message": "🚀 AI Agent running on Render!",
        "platform": "Render",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "ask": "POST /ask",
            "health": "GET /health",
        }
    }


@app.post("/ask")
async def ask_agent(request: Request):
    """
    Main endpoint để hỏi AI agent.
    
    Body: {"question": "your question here"}
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON body")
    
    question = body.get("question", "")
    if not question:
        raise HTTPException(422, "Field 'question' is required")
    
    # Call mock LLM (trong production, thay bằng OpenAI/Anthropic)
    answer = ask(question)
    
    return {
        "question": question,
        "answer": answer,
        "platform": "Render",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
def health():
    """
    Health check endpoint.
    Render sẽ ping endpoint này để check service còn sống không.
    Trả về 200 = healthy, non-200 = Render sẽ restart service.
    """
    uptime = round(time.time() - START_TIME, 1)
    
    return {
        "status": "ok",
        "uptime_seconds": uptime,
        "platform": "Render",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": os.getenv("ENVIRONMENT", "unknown"),
    }


@app.get("/info")
def info():
    """Thông tin về deployment"""
    return {
        "platform": "Render",
        "python_version": os.getenv("PYTHON_VERSION", "unknown"),
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "port": os.getenv("PORT", "unknown"),
    }


if __name__ == "__main__":
    # ✅ Render inject PORT env var — PHẢI đọc từ env
    port = int(os.getenv("PORT", 10000))
    print(f"🚀 Starting AI Agent on port {port} (from PORT env var)")
    print(f"📍 Platform: Render")
    print(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
