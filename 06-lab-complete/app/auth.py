from fastapi import Header, HTTPException
from app.config import settings
import logging

logger = logging.getLogger(__name__)

async def verify_api_key(x_api_key: str = Header(..., description="API Key for authentication")) -> str:
    """
    Verify API key from request header
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        str: Validated API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    # In production, validate against database
    # For this lab, we accept any non-empty key or the configured keys
    if not x_api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include X-API-Key header."
        )
    
    if len(x_api_key) < 10:
        logger.warning(f"Invalid API key format: {x_api_key[:5]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key format"
        )
    
    logger.info(f"API key validated: {x_api_key[:8]}...")
    return x_api_key
