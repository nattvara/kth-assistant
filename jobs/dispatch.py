from redis.exceptions import ConnectionError

from jobs.crawl.index_url import TIMEOUT as INDEX_URL_JOB_TIMEOUT
from cache.redis import get_redis_connection_sync
from jobs.crawl.index_url import job as index_url
from jobs.queues import get_index_queue
from config.logger import log
from db.models import Url


def dispatch_index_url(url: Url):
    try:
        redis = get_redis_connection_sync()
        q = get_index_queue(redis)
        q.enqueue(
            index_url,
            url,
            job_timeout=INDEX_URL_JOB_TIMEOUT
        )
    except ConnectionError:
        log().error("failed to connect to redis, couldn't dispatch job")
