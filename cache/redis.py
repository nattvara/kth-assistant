from redis.asyncio import Redis
from redis import Redis as RedisSync

import config.settings as settings


async def get_redis_connection() -> Redis:
    redis = Redis(
        host=settings.get_settings().REDIS_HOST,
        port=settings.get_settings().REDIS_PORT,
        decode_responses=True
    )
    await redis.ping()
    return redis


def get_redis_connection_sync() -> RedisSync:
    redis = RedisSync(
        host=settings.get_settings().REDIS_HOST,
        port=settings.get_settings().REDIS_PORT,
        decode_responses=True
    )
    redis.ping()
    return redis
