import redis.asyncio as redis
from app.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CostGuard:
    """Redis-based cost tracking with monthly limits"""
    
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
                logger.info("Redis cost guard initialized")
            except Exception as e:
                logger.warning(f"Redis connection failed, using in-memory fallback: {e}")
                self.use_redis = False
    
    async def check_cost_limit(self, api_key: str) -> bool:
        """
        Check if user is within monthly cost limit
        
        Args:
            api_key: API key to check
            
        Returns:
            bool: True if within limit, False if exceeded
        """
        usage = await self.get_usage(api_key)
        current_cost = usage.get("cost", 0)
        
        if current_cost >= settings.MONTHLY_COST_LIMIT:
            logger.warning(f"Cost limit exceeded for {api_key[:8]}... (${current_cost:.2f})")
            return False
        
        return True
    
    async def track_usage(self, api_key: str, cost: float):
        """
        Track API usage cost
        
        Args:
            api_key: API key
            cost: Cost of the request
        """
        key = f"cost:{api_key}:{self._get_month_key()}"
        
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.incrbyfloat(key, cost)
                # Expire at end of next month
                await self.redis_client.expire(key, 60 * 60 * 24 * 60)  # 60 days
                logger.info(f"Tracked ${cost:.4f} for {api_key[:8]}...")
                return
            except Exception as e:
                logger.error(f"Redis error, falling back to in-memory: {e}")
        
        # Fallback to in-memory
        if key not in self.fallback_store:
            self.fallback_store[key] = 0
        self.fallback_store[key] += cost
    
    async def get_usage(self, api_key: str) -> dict:
        """
        Get usage statistics for an API key
        
        Args:
            api_key: API key
            
        Returns:
            dict: Usage statistics
        """
        key = f"cost:{api_key}:{self._get_month_key()}"
        
        if self.use_redis and self.redis_client:
            try:
                cost = await self.redis_client.get(key)
                cost = float(cost) if cost else 0.0
                return {
                    "cost": cost,
                    "limit": settings.MONTHLY_COST_LIMIT,
                    "remaining": settings.MONTHLY_COST_LIMIT - cost,
                    "month": self._get_month_key()
                }
            except:
                pass
        
        # Fallback
        cost = self.fallback_store.get(key, 0.0)
        return {
            "cost": cost,
            "limit": settings.MONTHLY_COST_LIMIT,
            "remaining": settings.MONTHLY_COST_LIMIT - cost,
            "month": self._get_month_key()
        }
    
    async def get_total_users(self) -> int:
        """Get total number of users with tracked costs"""
        if self.use_redis and self.redis_client:
            try:
                keys = await self.redis_client.keys(f"cost:*:{self._get_month_key()}")
                return len(keys)
            except:
                pass
        
        return len(set(k.split(":")[1] for k in self.fallback_store.keys()))
    
    def _get_month_key(self) -> str:
        """Get current month key (YYYY-MM)"""
        return datetime.utcnow().strftime("%Y-%m")
    
    async def is_ready(self) -> bool:
        """Check if Redis is ready"""
        if not self.use_redis:
            return True
        
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
