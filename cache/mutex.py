from redis.asyncio import Redis


class LockAlreadyAcquiredException(Exception):
    pass


async def acquire_lock(redis: Redis, key: str, expire: int = 1000):
    acquired = await redis.set(key, "locked", nx=True, px=expire)
    if not acquired:
        raise LockAlreadyAcquiredException("Lock is already acquired.")


async def release_lock(redis: Redis, key: str):
    await redis.delete(key)
