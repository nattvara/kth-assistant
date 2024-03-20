from fastapi import APIRouter

from cache.redis import get_redis_connection
from db.connection import db

router = APIRouter()


def test_db() -> str:
    cursor = db.execute_sql('SELECT \'db is working fine.\' AS greeting;')
    result = cursor.fetchone()
    return result[0]


async def test_redis() -> str:
    redis = await get_redis_connection()
    await redis.set('greeting', 'redis is working fine.')
    return await redis.get('greeting')


@router.get('/health')
async def index():
    return {
        'database': test_db(),
        'redis': await test_redis(),
    }
