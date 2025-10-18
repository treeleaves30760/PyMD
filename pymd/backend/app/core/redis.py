"""Redis connection and cache management"""
import json
from typing import Any, Optional
from redis.asyncio import Redis, ConnectionPool

from pymd.backend.app.config import settings

# Redis connection pool
redis_pool: Optional[ConnectionPool] = None
redis_client: Optional[Redis] = None


async def init_redis():
    """Initialize Redis connection pool"""
    global redis_pool, redis_client
    redis_pool = ConnectionPool.from_url(
        settings.REDIS_URL,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        decode_responses=True,
    )
    redis_client = Redis(connection_pool=redis_pool)


async def close_redis():
    """Close Redis connections"""
    global redis_client, redis_pool
    if redis_client:
        await redis_client.close()
    if redis_pool:
        await redis_pool.disconnect()


def get_redis() -> Redis:
    """Get Redis client instance"""
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client


class CacheManager:
    """Redis cache manager"""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.redis.setex(key, ttl, value)

    async def delete(self, key: str):
        """Delete key from cache"""
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return bool(await self.redis.exists(key))

    async def increment(self, key: str) -> int:
        """Increment counter"""
        return await self.redis.incr(key)

    async def decrement(self, key: str) -> int:
        """Decrement counter"""
        return await self.redis.decr(key)
