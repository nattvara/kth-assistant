from urllib.parse import urlparse


CANVAS_DOMAIN = "canvas.kth.se"

CANVAS_PROFILE_PAGE = f"https://{CANVAS_DOMAIN}/profile"


def domain_is_canvas(url: str) -> bool:
    parsed_url = urlparse(url)
    return parsed_url.netloc == CANVAS_DOMAIN
