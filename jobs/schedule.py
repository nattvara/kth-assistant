from datetime import timedelta

from redis.exceptions import ConnectionError

from jobs.crawl.start_crawler_worker import TIMEOUT as START_CRAWLER_WORKER_TIMEOUT
from jobs.snapshot.capture_snapshots import TIMEOUT as CAPTURE_SNAPSHOTS_TIMEOUT
from jobs.crawl.start_crawler_worker import job as start_crawler_worker
from jobs.snapshot.capture_snapshots import job as capture_snapshots
from jobs.queues import get_crawler_queue, get_snapshots_queue
from cache.redis import get_redis_connection_sync
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

        q.enqueue_in(timedelta(seconds=start_in_seconds), start_crawler_worker, job_timeout=START_CRAWLER_WORKER_TIMEOUT)
    except ConnectionError:
        log().error("failed to connect to redis, couldn't start_crawler_worker job")


def schedule_job_capture_snapshots(start_in_seconds: int, should_empty: bool = False):
    try:
        redis = get_redis_connection_sync()
        q = get_snapshots_queue(redis)
        if should_empty:
            log().info("emptying snapshots queue.")
            registry = q.scheduled_job_registry
            for job_id in registry.get_job_ids():
                registry.remove(job_id)

        q.enqueue_in(timedelta(seconds=start_in_seconds), capture_snapshots, job_timeout=CAPTURE_SNAPSHOTS_TIMEOUT)
    except ConnectionError:
        log().error("failed to connect to redis, couldn't schedule capture_snapshots job")
