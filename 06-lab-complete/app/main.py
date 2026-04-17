from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from contextlib import asynccontextmanager
import signal
import sys
import logging
from datetime import datetime

from app.config import settings
from app.auth import verify_api_key
from app.rate_limiter import RateLimiter
from app.cost_guard import CostGuard
from utils.mock_llm import MockLLM

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
rate_limiter = None
cost_guard = None
llm = None
shutdown_event = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown"""
    global rate_limiter, cost_guard, llm
    
    # Startup
    logger.info("Starting application...")
    rate_limiter = RateLimiter()
    cost_guard = CostGuard()
    llm = MockLLM()
    
    # Setup graceful shutdown
    def signal_handler(signum, frame):
        global shutdown_event
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        shutdown_event = True
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    if rate_limiter:
        await rate_limiter.close()
    if cost_guard:
        await cost_guard.close()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="Production AI Agent",
    description="Production-ready conversational AI with auth, rate limiting, and cost protection",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    tokens_used: int
    cost: float

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

class ReadinessResponse(BaseModel):
    ready: bool
    services: dict

# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve web UI"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint - always returns 200 if app is running"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )

@app.get("/readiness", response_model=ReadinessResponse)
async def readiness():
    """Readiness check - verifies all dependencies are ready"""
    services = {
        "redis": await rate_limiter.is_ready() if rate_limiter else False,
        "cost_guard": await cost_guard.is_ready() if cost_guard else False,
        "llm": llm is not None
    }
    
    ready = all(services.values())
    
    return ReadinessResponse(
        ready=ready,
        services=services
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Chat endpoint with authentication, rate limiting, and cost protection
    
    Requires:
    - X-API-Key header for authentication
    - Rate limit: 10 requests per minute per API key
    - Cost limit: $10 per month per API key
    """
    try:
        # Check rate limit
        if not await rate_limiter.check_rate_limit(api_key):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Maximum 10 requests per minute."
            )
        
        # Check cost limit
        if not await cost_guard.check_cost_limit(api_key):
            raise HTTPException(
                status_code=402,
                detail="Monthly cost limit exceeded. Maximum $10 per month."
            )
        
        # Generate response
        response_text = llm.generate(request.message)
        
        # Calculate cost (mock: $0.002 per request)
        tokens_used = len(request.message.split()) + len(response_text.split())
        cost = 0.002
        
        # Track cost
        await cost_guard.track_usage(api_key, cost)
        
        return ChatResponse(
            response=response_text,
            tokens_used=tokens_used,
            cost=cost
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/usage/{api_key}")
async def get_usage(
    api_key: str,
    verified_key: str = Depends(verify_api_key)
):
    """Get usage statistics for an API key"""
    if api_key != verified_key:
        raise HTTPException(status_code=403, detail="Cannot view other users' usage")
    
    usage = await cost_guard.get_usage(api_key)
    remaining_requests = await rate_limiter.get_remaining_requests(api_key)
    
    return {
        "api_key": api_key[:8] + "..." + api_key[-4:],
        "monthly_cost": usage.get("cost", 0),
        "monthly_limit": 10.0,
        "remaining_budget": 10.0 - usage.get("cost", 0),
        "requests_this_minute": 10 - remaining_requests,
        "rate_limit": "10 requests/minute"
    }

@app.get("/metrics")
async def metrics(api_key: str = Depends(verify_api_key)):
    """Get system metrics (admin only)"""
    if api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {
        "total_users": await cost_guard.get_total_users(),
        "total_requests": await rate_limiter.get_total_requests(),
        "uptime": "N/A",  # Would track in production
        "redis_connected": await rate_limiter.is_ready()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
