from redis.asyncio import Redis

import config.settings as settings


async def get_redis_connection():
    redis = Redis(
        host=settings.get_settings().REDIS_HOST,
        port=settings.get_settings().REDIS_PORT,
        decode_responses=True
    )
    await redis.ping()
    return redis
