from redis import Redis
from rq import Queue


def get_crawler_queue(redis_connection: Redis) -> Queue:
    queue = Queue('crawler', connection=redis_connection)
    return queue
