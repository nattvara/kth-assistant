from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from jobs.schedule import schedule_job_start_crawler_worker, schedule_job_capture_snapshots
import config.settings as settings
from http_api.routers import (
    websocket,
    feedback,
    sessions,
    health,
    index,
    chat,
)
from config.logger import log


def get_app():
    app = FastAPI(title=settings.get_settings().NAME, openapi_url=None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip('/') for origin in settings.get_settings().BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(index.router)
    app.include_router(websocket.router)
    app.include_router(sessions.router)
    app.include_router(chat.router)
    app.include_router(health.router)
    app.include_router(feedback.router)

    return app


def main():
    log().info('http api is starting')

    app = get_app()

    num_crawler_workers = settings.get_settings().NUMBER_OF_CRAWLER_WORKERS

    log().info("starting 1 snapshot worker")
    schedule_job_capture_snapshots(1, True)

    log().info(f"starting {num_crawler_workers} crawler workers")
    schedule_job_start_crawler_worker(1, True)
    for i in range(num_crawler_workers - 1):
        schedule_job_start_crawler_worker(1, False)

    return app
