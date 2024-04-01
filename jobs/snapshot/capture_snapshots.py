from db.actions.snapshot import find_latest_snapshot_for_course
from services.crawler.crawler import CrawlerService
from config.logger import log
from db.models import Course

# 1 minute timeout
TIMEOUT = 60


def start_job_again_in(seconds: int):
    from jobs.schedule import schedule_job_capture_snapshots
    schedule_job_capture_snapshots(seconds)


async def job():
    try:
        for course in Course.select():
            snapshot = find_latest_snapshot_for_course(course)
            if snapshot is None:
                log().info(f"no snapshots existed for course: {course.canvas_id}, creating first snapshot.")
                CrawlerService.create_snapshot(course)
                continue

            if CrawlerService.snapshot_expired(snapshot, course):
                log().info(f"last snapshot for course {course.canvas_id} expired, creating new snapshot.")
                CrawlerService.create_snapshot(course)
    finally:
        start_job_again_in(60)
