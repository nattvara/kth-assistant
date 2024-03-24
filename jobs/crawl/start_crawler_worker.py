from playwright.async_api import Browser, BrowserContext, Page
from redis.asyncio import Redis
import playwright.async_api

from cache.mutex import LockAlreadyAcquiredException
from services.crawler.crawler import CrawlerService
from config.logger import log
import cache.redis


def get_crawler_service(redis: Redis, browser: Browser, context: BrowserContext, page: Page) -> CrawlerService:
    return CrawlerService(redis, browser, context, page)


def start_job_again_in(seconds: int):
    from jobs.schedule import schedule_job_start_crawler_worker
    schedule_job_start_crawler_worker(seconds)


async def job():
    try:
        async with playwright.async_api.async_playwright() as pl:
            browser = await pl.chromium.launch(headless=True)
            context = await browser.new_context(viewport={'width': 800, 'height': 1000})
            page = await context.new_page()

            redis = await cache.redis.get_redis_connection()
            service = get_crawler_service(redis, browser, context, page)

            while service.has_next():
                try:
                    url = await service.checkout()
                    await service.crawl_url(url)
                except LockAlreadyAcquiredException:
                    log().debug("Found a lock on the url. Skipping.")

            await redis.aclose()
    finally:
        log().info(f"start_crawler_worker complete. enqueuing next job in 60 seconds.")
        start_job_again_in(60)
