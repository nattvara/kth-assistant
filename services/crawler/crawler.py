from playwright.async_api import Browser, BrowserContext, Page
from playwright.async_api import Error as PlaywrightError
from redis.asyncio import Redis
import arrow

from db.actions.url import get_most_recent_url, exists_any_unvisited_urls_in_snapshot
from db.actions.snapshot import all_snapshots_of_course_in_most_recent_order
from db.models import Course, Snapshot, Url
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
            response = await self.page.goto(url.href, wait_until='load')
            await response.body()
            await self.page.wait_for_load_state('load')
        except PlaywrightError as e:
            url.state = Url.States.FAILED
            url.save()
            raise e

        url.state = Url.States.VISITED
        url.save()
