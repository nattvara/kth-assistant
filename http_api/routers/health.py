from fastapi import APIRouter, Response
from pydantic import BaseModel

from cache.redis import get_redis_connection
import services.index.opensearch as search
from db.connection import db

router = APIRouter()


class HealthResponse(BaseModel):
    database: str
    redis: str
    search_index: str


def test_db() -> str:
    cursor = db.execute_sql('SELECT \'db is working fine.\' AS greeting;')
    result = cursor.fetchone()
    return result[0]


async def test_redis() -> str:
    redis = await get_redis_connection()
    await redis.set('greeting', 'redis is working fine.')
    return await redis.get('greeting')


def test_opensearch() -> str:
    client = search.get_client()
    return search.health_check(client)


@router.get('/health', response_model=HealthResponse)
async def index(response: Response):
    try:
        redis_result = await test_redis()
    except:  # noqa
        redis_result = 'redis is NOT working.'
        response.status_code = 503

    try:
        db_result = test_db()
    except:  # noqa
        db_result = 'db is NOT working.'
        response.status_code = 503

    try:
        test_opensearch()
        opensearch_result = 'search index is working fine.'
    except:  # noqa
        opensearch_result = 'search index is NOT working.'
        response.status_code = 503

    health_response = HealthResponse(
        database=db_result,
        redis=redis_result,
        search_index=opensearch_result,
    )
    return health_response
