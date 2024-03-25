from playwright.async_api import Browser, BrowserContext, Page

from services.download.text import extract_text_from_html, extract_text_from_pdf_file
from db.actions.url import find_url_referencing_content_in_snapshot
from services.crawler.url_filters import domain_is_canvas
from db.actions.content import find_content_with_sha
import services.download.canvas as canvas
import services.download.web as web
import services.download.pdf as pdf
from db.models import Url, Content
from config.logger import log


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
        log().info(f"Saving content from {url.href}")

        if url.state != Url.States.VISITED:
            raise InvalidUrlStateException(f"url must be in {Url.States.VISITED} to be"
                                           f"downloaded, url was in {url.state}")

        if url.is_download:
            content = await self._save_pdf_url_content(url)
        elif domain_is_canvas(url.href):
            content = await self._save_canvas_url_content(url)
        else:
            content = await self._save_web_url_content(url)

        same_content = find_content_with_sha(content.make_sha())
        if same_content is not None:
            other_url = find_url_referencing_content_in_snapshot(url.snapshot, same_content)
            if other_url is not None:
                url.content = other_url.content
                url.content_is_duplicate = True
                url.save()
                return

        content.save()
        url.content = content
        url.save()

    async def _save_pdf_url_content(self, url: Url):
        content_filepath, filename = pdf.download_content(url)
        text = extract_text_from_pdf_file(content_filepath)
        content = Content(text=text, name=filename)
        return content

    async def _save_canvas_url_content(self, url: Url):
        html, title = await canvas.download_content(url, self.page)
        text = extract_text_from_html(html)
        content = Content(text=text, name=title)
        return content

    async def _save_web_url_content(self, url: Url):
        html, title = await web.download_content(url, self.page)
        text = extract_text_from_html(html)
        content = Content(text=text, name=title)
        return content
