from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application configuration"""
    
    # Server
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "true").lower() == "true"
    
    # Authentication
    API_KEY: str = os.getenv("API_KEY", "test-api-key-12345")
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "admin-key-67890")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    # Cost Protection
    MONTHLY_COST_LIMIT: float = float(os.getenv("MONTHLY_COST_LIMIT", "10.0"))
    
    # OpenAI (optional)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
