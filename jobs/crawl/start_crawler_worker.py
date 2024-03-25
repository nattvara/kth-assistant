from playwright.async_api import Browser, BrowserContext, Page
from redis.asyncio import Redis
import playwright.async_api

import services.crawler.playwright as playwright_helper
from services.download.download import DownloadService
from cache.mutex import LockAlreadyAcquiredException
from services.crawler.crawler import CrawlerService
from config.logger import log
from db.models import Url
import cache.redis

# 60 minute timeout
TIMEOUT = 60 * 60


def get_crawler_service(redis: Redis, browser: Browser, context: BrowserContext, page: Page) -> CrawlerService:
    return CrawlerService(redis, browser, context, page)


def get_download_service(browser: Browser, context: BrowserContext, page: Page) -> DownloadService:
    return DownloadService(browser, context, page)


def start_job_again_in(seconds: int):
    from jobs.schedule import schedule_job_start_crawler_worker
    schedule_job_start_crawler_worker(seconds)


async def run_worker():
    async with playwright.async_api.async_playwright() as pl:
        browser, context, page = await playwright_helper.get_logged_in_browser_context_and_page(pl)

        redis = await cache.redis.get_redis_connection()
        crawler_service = get_crawler_service(redis, browser, context, page)
        download_service = get_download_service(browser, context, page)

        while crawler_service.has_next():
            try:
                url = await crawler_service.checkout()
                await crawler_service.crawl_url(url)

                url.refresh()
                if url.state == Url.States.VISITED:
                    await download_service.save_url_content(url)
            except LockAlreadyAcquiredException:
                log().debug("Found a lock on the url. Skipping.")

        await redis.aclose()


async def job():
    try:
        await run_worker()
    finally:
        log().info(f"start_crawler_worker complete. enqueuing next job in 60 seconds.")
        start_job_again_in(60)
