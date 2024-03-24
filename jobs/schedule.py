from datetime import timedelta

from redis.exceptions import ConnectionError

from jobs.crawl.start_crawler_worker import job as start_crawler_worker
from cache.redis import get_redis_connection_sync
from jobs.queues import get_crawler_queue
from config.logger import log


def schedule_job_start_crawler_worker(start_in_seconds: int, should_empty: bool = False):
    try:
        redis = get_redis_connection_sync()
        q = get_crawler_queue(redis)
        if should_empty:
            log().info("emptying crawler queue.")
            registry = q.scheduled_job_registry
            for job_id in registry.get_job_ids():
                registry.remove(job_id)

        q.enqueue_in(timedelta(seconds=start_in_seconds), start_crawler_worker)
    except ConnectionError:
        log().error("failed to connect to redis, couldn't schedule crawler job")
