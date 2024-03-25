import asyncio

from playwright.async_api import Browser, BrowserContext, Page
from playwright.async_api import Error as PlaywrightError
from redis.asyncio import Redis
import arrow

from db.actions.url import get_most_recent_url, exists_any_unvisited_urls_in_snapshot
from db.actions.snapshot import all_snapshots_of_course_in_most_recent_order
import services.crawler.content_extraction as content_extraction
from services.crawler.url_filters import domain_is_canvas, get_domain
import services.crawler.url_filters as url_filters
from db.models import Course, Snapshot, Url
import config.settings as settings
from config.logger import log
import cache.mutex as mutex


class NoUnvisitedUrlException(Exception):
    pass


class NoValidSnapshotException(Exception):
    pass


class CrawlerService:

    def __init__(
            self,
            redis: Redis,
            browser: Browser,
            context: BrowserContext,
            page: Page
    ):
        self.redis = redis
        self.browser = browser
        self.context = context
        self.page = page

    @staticmethod
    def create_snapshot(course: Course) -> Snapshot:
        snapshot = Snapshot(course=course)
        snapshot.save()

        root_url = Url(
            snapshot=snapshot,
            href=f"https://canvas.kth.se/courses/{course.canvas_id}",
            root=True,
            distance=0,
        )
        root_url.save()

        return snapshot

    @staticmethod
    def snapshot_expired(snapshot: Snapshot, course: Course) -> bool:
        if arrow.now() >= snapshot.created_at.shift(minutes=course.snapshot_lifetime_in_mins):
            return True
        return False

    @staticmethod
    def current_snapshot(course: Course) -> Snapshot:
        snapshots = all_snapshots_of_course_in_most_recent_order(course)
        for snapshot in snapshots:
            if exists_any_unvisited_urls_in_snapshot(snapshot) is True:
                continue
            else:
                return snapshot

        raise NoValidSnapshotException(f"Could not find a valid snapshot of course with id {course.canvas_id}")

    async def checkout(self) -> Url:
        url = self.next()

        lock_name = f'url_{url.id}'
        await mutex.acquire_lock(self.redis, lock_name)

        try:
            url.state = Url.States.CRAWLING
            url.save()
        finally:
            await mutex.release_lock(self.redis, lock_name)

        return url

    def next(self) -> Url:
        url = get_most_recent_url()
        if url is None:
            raise NoUnvisitedUrlException("no unvisited urls was found")
        return url

    def has_next(self) -> bool:
        url = get_most_recent_url()
        return url is not None

    async def crawl_url(self, url: Url):
        try:
            log().info(f"crawling url {url.href}")

            response = await self.page.goto(url.href, wait_until='load')
            await self.page.wait_for_load_state('load')
            await asyncio.sleep(2)

            if 200 <= response.status <= 399:
                url.response_was_ok = True
            else:
                url.response_was_ok = False

            if url.href.endswith('.pdf'):
                url.is_download = True

            links = await content_extraction.get_all_links_from_page(self.page)
            for link in links:
                if get_domain(link) in url_filters.DOMAIN_DENY_LIST:
                    log().info(f"ignoring href {link} since the domain {get_domain(link)} was found"
                               f"on url domain deny list")
                    continue

                if url.distance >= settings.get_settings().MAX_CRAWL_DISTANCE_ALLOWED:
                    log().info(f"ignoring href {link} since it was found"
                               f"on url {url.href} with distance {url.distance}")
                    continue

                # if we've gotten this far we have no reason not to register the domain
                self.register_url(href=link, found_on=url)

        except PlaywrightError as e:
            if 'net::ERR_ABORTED' in str(e):
                log().info(f'Download triggered at {url.href}, continuing with next link.')
                url.is_download = True
            else:
                url.state = Url.States.FAILED
                url.save()
                raise e

        url.state = Url.States.VISITED
        url.save()

    def register_url(self, href: str, found_on: Url):
        distance = found_on.distance
        if not domain_is_canvas(href):
            distance += 1

        url = Url(
            snapshot=found_on.snapshot,
            href=href,
            root=False,
            distance=distance,
        )
        url.save()
