from urllib.parse import urljoin
import asyncio
import re

from playwright.async_api import Page

from db.models import Url


async def download_content(url: Url, page: Page):
    await page.goto(url.href)
    await page.wait_for_load_state('load')
    await asyncio.sleep(2)

    content = await page.query_selector('#content')
    content_html = await content.inner_html()
    title = await page.title()

    def make_absolute(m):
        return f'src="{urljoin(url.href, m.group(1))}"'

    content_html = re.sub(r'src="([^"]+)"', make_absolute, content_html)

    return content_html, title
