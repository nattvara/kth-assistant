from urllib.parse import urlparse


CANVAS_DOMAIN = "canvas.kth.se"

CANVAS_PROFILE_PAGE = f"https://{CANVAS_DOMAIN}/profile"

DOMAIN_DENY_LIST = {
    "app.kth.se": True,
}

DENY_URLS_THAT_STARTS_WITH = {
    "https://canvas.kth.se/search": True,
    "https://www.instructure.com/policies": True,
    "https://canvas.kth.se/#": True,
    "https://canvas.kth.se/us/": True,
    "https://canvas.kth.se/policy": True,
    "https://canvas.kth.se/network": True,
    "https://canvas.kth.se/profile": True,
    "https://canvas.kth.se/images": True,
    "https://canvas.kth.se/about": True,
    "https://canvas.kth.se/feeds": True,
    "https://canvas.kth.se/contact": True,
    "https://canvas.kth.se/fall18seminar": True,
    "https://canvas.kth.se/Bio": True,
    "https://canvas.kth.se/Papers": True,
    "https://canvas.kth.se/informal": True,
    "https://canvas.kth.se/commodore1988": True,
    "https://canvas.kth.se/Courses": True,
    "https://canvas.kth.se/boaz_pronounce.m4a": True,
    "https://canvas.kth.se/courses/#content": True,
    "https://canvas.kth.se/groups": True,
}

DENY_URLS_THAT_CONTAINS = {
    "?comment_id=": True,
    "discussion_topics/new": True,
}


def get_domain(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.netloc


def domain_is_canvas(url: str) -> bool:
    return get_domain(url) == CANVAS_DOMAIN


def link_begins_with_deny_listed_string(url: str) -> bool:
    for key in DENY_URLS_THAT_STARTS_WITH.keys():
        if url.startswith(key):
            return True
    return False


def link_contains_deny_listed_string(url: str) -> bool:
    for key in DENY_URLS_THAT_CONTAINS.keys():
        if key in url:
            return True
    return False
