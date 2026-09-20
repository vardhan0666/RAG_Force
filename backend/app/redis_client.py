import redis.asyncio as aioredis
from app.config import settings

redis_pool = aioredis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
)


def get_redis() -> aioredis.Redis:
    return aioredis.Redis(connection_pool=redis_pool)