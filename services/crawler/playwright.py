from playwright.async_api import Browser, BrowserContext, Page
from playwright.async_api import Playwright

from services.crawler.url_filters import CANVAS_DOMAIN, CANVAS_PROFILE_PAGE
from db.actions.cookie import find_cookie_by_identifier
import config.settings as settings
from config.logger import log


class PlaywrightCookieException(Exception):
    pass


class PlaywrightCookieValidationException(Exception):
    pass


async def get_logged_in_browser_context_and_page(playwright: Playwright) -> (Browser, BrowserContext, Page):
    browser = await playwright.chromium.launch(headless=settings.get_settings().CRAWLER_MODE_IS_HEADLESS)
    context = await browser.new_context(viewport={'width': 800, 'height': 1000})

    cookie = find_cookie_by_identifier(settings.get_settings().COOKIE_IDENTIFIER)
    if cookie is None:
        raise PlaywrightCookieException(f"could not find any cookie"
                                        f"with identifier: {settings.get_settings().COOKIE_IDENTIFIER}")

    cookies = cookie.value.split('; ')

    prepared_cookies = []
    for cookie in cookies:
        name, value = cookie.strip().split('=', 1)
        prepared_cookies.append({
            'name': name,
            'value': value,
            'domain': CANVAS_DOMAIN,
            'path': '/',
            'expires': -1
        })

    await context.add_cookies(prepared_cookies)

    # if this profile page can be loaded and verified we know
    # the cookie is valid
    page = await _ensure_profile_page_can_be_loaded(context)

    return browser, context, page


async def _ensure_profile_page_can_be_loaded(context: BrowserContext) -> Page:
    page = await context.new_page()
    search_string = settings.get_settings().CANVAS_PROFILE_PAGE_VALIDATION_SEARCH_STRING

    try:
        await page.goto(CANVAS_PROFILE_PAGE, wait_until='load')
        await page.wait_for_load_state('load')

        log().info(f"looking for the string '{search_string}' on the profile page")
        locator = page.locator(f"text='{search_string}'")
        await locator.wait_for(state="visible", timeout=5000)

        return page
    except Exception:
        raise PlaywrightCookieValidationException("failed to find string on profile page. cookie is most"
                                                  " likely expired.")
