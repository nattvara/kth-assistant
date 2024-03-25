from urllib.parse import urlparse


CANVAS_DOMAIN = "canvas.kth.se"

CANVAS_PROFILE_PAGE = f"https://{CANVAS_DOMAIN}/profile"

DOMAIN_DENY_LIST = {
    "app.kth.se": True,
}


def get_domain(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.netloc


def domain_is_canvas(url: str) -> bool:
    return get_domain(url) == CANVAS_DOMAIN
