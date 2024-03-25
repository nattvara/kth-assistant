from playwright.async_api import Browser, BrowserContext, Page

from services.crawler.url_filters import domain_is_canvas
import services.download.canvas as canvas
from db.models import Url, Content


class InvalidUrlStateException(Exception):
    pass


class DownloadService:

    def __init__(
            self,
            browser: Browser,
            context: BrowserContext,
            page: Page
    ):
        self.browser = browser
        self.context = context
        self.page = page

    async def save_url_content(self, url: Url):
        if url.state != Url.States.VISITED:
            raise InvalidUrlStateException(f"url must be in {Url.States.VISITED} to be"
                                           f"downloaded, url was in {url.state}")

        if domain_is_canvas(url.href):
            content = await self._save_canvas_url_content(url)

        url.content = content
        url.save()

    async def _save_canvas_url_content(self, url: Url):
        html = await canvas.download_content(url, self.page)
        content = Content(text=html)
        content.save()
        return content
