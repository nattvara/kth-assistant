import asyncio

from playwright.async_api import Page

from db.models import Url


async def download_content(url: Url, page: Page):
    await page.goto(url.href)
    await page.wait_for_load_state('load')
    await asyncio.sleep(2)

    content_html = await page.inner_html('body')
    title = await page.title()

    return content_html, title
