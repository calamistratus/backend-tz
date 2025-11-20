from redis import asyncio as redis

from settings import settings

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0,
    decode_responses=True,
    password=settings.redis_password
)