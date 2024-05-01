from urllib.parse import urlparse
import re


CANVAS_DOMAIN = "canvas.kth.se"

KATTIS_KTH_DOMAIN = "kth.kattis.com"

KATTIS_OPEN_DOMAIN = "open.kattis.com"

GOOGLE_DOCS = "docs.google.com"

CANVAS_PROFILE_PAGE = f"https://{CANVAS_DOMAIN}/profile"

DOMAIN_DENY_LIST = {
    "app.kth.se": True,
    "community.canvaslms.com": True,
    "youtube.com": True,
    "youtu.be": True,
    "kth-se.zoom.us": True,
    "support.kattis.com": True,
    "docs.oracle.com": True,
    "oracle.com": True,
    "intra.kth.se": True,
}

DENY_URLS_THAT_STARTS_WITH = {
    "mailto:": True,
    "tel:": True,
    "javascript:": True,
    "data:": True,
    "file:": True,
    "ftp:": True,
    "blob:": True,
    "ws:": True,
    "wss:": True,
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
    "https://canvas.kth.se/conversations": True,
    "https://canvas.kth.se/accounts": True,
    "https://canvas.kth.se/calendar": True,
    "https://www.kth.se/eecs": True,
    "http://www.kth.se/eecs": True,
}

DENY_URLS_THAT_CONTAINS = {
    "?comment_id=": True,
    "discussion_topics/new": True,
}

DENY_URLS_THAT_MATCHES_REGEX = [
    r'https:\/\/canvas\.kth\.se\/[^\/]+\/[^\/]+\/grades\/',
    r'https://canvas\.kth\.se/courses/\d+/groups',
    r'https://canvas\.kth\.se/courses/\d+/user_services',
    r'https://canvas\.kth\.se/courses/\d+/users',
    r'https://canvas\.kth\.se/courses/\d+/grades',
    r'https://canvas\.kth\.se/courses/\d+/assignments/\d+/submissions/.*',
]

DENY_URLS_THAT_MATCHES_STRING_EXACTLY = {
    "https://canvas.kth.se/courses": True,
    "https://canvas.kth.se/courses/": True,
    "https://canvas.kth.se": True,
    "https://canvas.kth.se/": True,
    "https://kth.kattis.com": True,
    "https://kth.kattis.com/": True,
    "http://kth.kattis.com": True,
    "http://kth.kattis.com/": True,
    "https://kth.kattis.com/courses": True,
    "https://kth.kattis.com/courses/": True,
    "https://www.kth.se/student": True,
    "https://www.kth.se/student/": True,
    "https://www.kth.se": True,
    "https://www.kth.se/": True,
    "https://www.kth.se/en": True,
    "https://www.kth.se/en/": True,
    "https://www.kth.se/en/student": True,
    "https://www.kth.se/en/student/": True,
}


def get_domain(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.netloc


def domain_is_canvas(url: str) -> bool:
    return get_domain(url) == CANVAS_DOMAIN


def domain_is_kattis(url: str) -> bool:
    return get_domain(url) == KATTIS_KTH_DOMAIN or get_domain(url) == KATTIS_OPEN_DOMAIN


def domain_is_google_docs(url: str) -> bool:
    return get_domain(url) == GOOGLE_DOCS


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


def link_matches_any_deny_listed_regex(url: str) -> bool:
    for pattern in DENY_URLS_THAT_MATCHES_REGEX:
        if re.match(pattern, url):
            return True
    return False


def link_belongs_to_another_canvas_course_room(url: str, canvas_id: str) -> bool:
    def extract_course_id(url: str) -> str:
        regex = r"https://canvas\.kth\.se/courses/([^/]+)"
        match = re.search(regex, url)
        if match:
            return match.group(1)
        else:
            return None

    if not domain_is_canvas(url):
        return False

    course_id = extract_course_id(url)
    if course_id is None:
        return False

    if course_id != canvas_id:
        return True

    return False
