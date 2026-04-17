import redis.asyncio as redis
from app.config import settings
import logging
import time

logger = logging.getLogger(__name__)

class RateLimiter:
    """Redis-based rate limiter with fallback to in-memory"""
    
    def __init__(self):
        self.redis_client = None
        self.fallback_store = {}  # In-memory fallback
        self.use_redis = settings.REDIS_ENABLED
        
        if self.use_redis:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                logger.info("Redis rate limiter initialized")
            except Exception as e:
                logger.warning(f"Redis connection failed, using in-memory fallback: {e}")
                self.use_redis = False
    
    async def check_rate_limit(self, api_key: str) -> bool:
        """
        Check if request is within rate limit
        
        Args:
            api_key: API key to check
            
        Returns:
            bool: True if within limit, False if exceeded
        """
        key = f"rate_limit:{api_key}"
        
        if self.use_redis and self.redis_client:
            try:
                # Use Redis sliding window
                current_time = int(time.time())
                window_start = current_time - settings.RATE_LIMIT_WINDOW
                
                # Remove old entries
                await self.redis_client.zremrangebyscore(key, 0, window_start)
                
                # Count requests in window
                count = await self.redis_client.zcard(key)
                
                if count >= settings.RATE_LIMIT_REQUESTS:
                    logger.warning(f"Rate limit exceeded for {api_key[:8]}...")
                    return False
                
                # Add current request
                await self.redis_client.zadd(key, {str(current_time): current_time})
                await self.redis_client.expire(key, settings.RATE_LIMIT_WINDOW)
                
                return True
                
            except Exception as e:
                logger.error(f"Redis error, falling back to in-memory: {e}")
                return self._check_rate_limit_memory(api_key)
        else:
            return self._check_rate_limit_memory(api_key)
    
    def _check_rate_limit_memory(self, api_key: str) -> bool:
        """In-memory rate limiting fallback"""
        current_time = time.time()
        
        if api_key not in self.fallback_store:
            self.fallback_store[api_key] = []
        
        # Remove old entries
        self.fallback_store[api_key] = [
            t for t in self.fallback_store[api_key]
            if current_time - t < settings.RATE_LIMIT_WINDOW
        ]
        
        if len(self.fallback_store[api_key]) >= settings.RATE_LIMIT_REQUESTS:
            return False
        
        self.fallback_store[api_key].append(current_time)
        return True
    
    async def get_remaining_requests(self, api_key: str) -> int:
        """Get remaining requests in current window"""
        key = f"rate_limit:{api_key}"
        
        if self.use_redis and self.redis_client:
            try:
                current_time = int(time.time())
                window_start = current_time - settings.RATE_LIMIT_WINDOW
                await self.redis_client.zremrangebyscore(key, 0, window_start)
                count = await self.redis_client.zcard(key)
                return max(0, settings.RATE_LIMIT_REQUESTS - count)
            except:
                pass
        
        # Fallback
        if api_key in self.fallback_store:
            current_time = time.time()
            valid_requests = [
                t for t in self.fallback_store[api_key]
                if current_time - t < settings.RATE_LIMIT_WINDOW
            ]
            return max(0, settings.RATE_LIMIT_REQUESTS - len(valid_requests))
        
        return settings.RATE_LIMIT_REQUESTS
    
    async def get_total_requests(self) -> int:
        """Get total requests across all users"""
        if self.use_redis and self.redis_client:
            try:
                keys = await self.redis_client.keys("rate_limit:*")
                total = 0
                for key in keys:
                    total += await self.redis_client.zcard(key)
                return total
            except:
                pass
        
        return sum(len(v) for v in self.fallback_store.values())
    
    async def is_ready(self) -> bool:
        """Check if Redis is ready"""
        if not self.use_redis:
            return True  # In-memory is always ready
        
        try:
            if self.redis_client:
                await self.redis_client.ping()
                return True
        except:
            pass
        
        return False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
