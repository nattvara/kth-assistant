from urllib.parse import urlparse, urljoin

from playwright.async_api import Page


async def get_all_links_from_page(page: Page):
    current_full_url = await page.evaluate('window.location.href')

    # js function to capture some surrounding context of a link
    link_info_script = """
    Array.from(document.querySelectorAll('a:not(.ic-app-header__menu-list-link)')).map(link => {
        return {
            href: link.getAttribute('href'),
            text: link.textContent,
            surroundingText: link.parentElement ? link.parentElement.textContent : ''
        };
    });
    """

    links_info = await page.evaluate(link_info_script)

    links = []
    for info in links_info:
        href = info['href']

        if not urlparse(href).netloc:
            parsed_url = urlparse(current_full_url)
            base_path = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
            base_path = base_path[:base_path.rfind('/')+1] if '/' in parsed_url.path else base_path

            resolved_url = urljoin(base_path, href)
        else:
            # If the href is already a fully qualified URL, use it as it is
            resolved_url = href

        links.append(resolved_url)

    return links
