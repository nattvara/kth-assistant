from jobs.schedule import schedule_job_capture_snapshots, schedule_job_start_crawler_worker
import config.settings as settings
from config.logger import log


def main():
    num_crawler_workers = settings.get_settings().NUMBER_OF_CRAWLER_WORKERS

    log().info("starting 1 snapshot worker")
    schedule_job_capture_snapshots(1, True)

    log().info(f"starting {num_crawler_workers} crawler workers")
    schedule_job_start_crawler_worker(1, True)
    for i in range(num_crawler_workers - 1):
        schedule_job_start_crawler_worker(1, False)


if __name__ == '__main__':
    main()
