from playwright.async_api import Browser, BrowserContext, Page
from redis.asyncio import Redis
import playwright.async_api

import services.crawler.playwright as playwright_helper
from services.download.download import DownloadService
from cache.mutex import LockAlreadyAcquiredException
from services.crawler.crawler import CrawlerService
from services.index.index import IndexService
from jobs.dispatch import dispatch_index_url
from config.logger import log
from db.models import Url
import cache.redis

# 3 hour timeout
TIMEOUT = 3 * 60 * 60


def get_crawler_service(redis: Redis, browser: Browser, context: BrowserContext, page: Page) -> CrawlerService:
    return CrawlerService(redis, browser, context, page)


def get_download_service(browser: Browser, context: BrowserContext, page: Page) -> DownloadService:
    return DownloadService(browser, context, page)


def get_index_service() -> IndexService:
    return IndexService()


def start_job_again_in(seconds: int):
    from jobs.schedule import schedule_job_start_crawler_worker
    schedule_job_start_crawler_worker(seconds)


async def run_worker():
    async with playwright.async_api.async_playwright() as pl:
        try:
            browser, context, page = await playwright_helper.get_logged_in_browser_context_and_page(pl)
        except playwright_helper.PlaywrightCookieValidationException:
            log().error("Couldn't verify the browser was logged in, ensure the cookie is valid. Exiting job for now")
            return

        redis = await cache.redis.get_redis_connection()
        crawler_service = get_crawler_service(redis, browser, context, page)
        download_service = get_download_service(browser, context, page)

        while crawler_service.has_next():
            try:
                url = await crawler_service.checkout()
                await crawler_service.crawl_url(url)

                url.refresh()
                if url.state == Url.States.VISITED:
                    try:
                        await download_service.save_url_content(url)

                        url.refresh()

                        if url.content_is_duplicate:
                            url.state = Url.States.NOT_ADDED_TO_INDEX
                            url.save()
                        elif url.response_was_ok or url.is_download:
                            url.state = Url.States.WAITING_TO_INDEX
                            url.save()
                            dispatch_index_url(url)
                        else:
                            url.state = Url.States.NOT_ADDED_TO_INDEX
                            url.save()
                    except Exception as e:
                        log().error(e)
                        log().error(f"failed to download url: {url.href}")
                        url.refresh()
                        url.state = Url.States.FAILED
                        url.save()

            except LockAlreadyAcquiredException:
                log().debug("Found a lock on the url. Skipping.")

        await redis.aclose()


async def job():
    try:
        await run_worker()
    finally:
        log().info("start_crawler_worker complete. enqueuing next job in 60 seconds.")
        start_job_again_in(60)
