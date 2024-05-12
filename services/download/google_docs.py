import re

from services.download import pdf
from config.logger import log
from db.models import Url


class GoogleDocsException(Exception):
    pass


def can_be_exported(url: Url) -> bool:
    if "docs.google.com/presentation" in url.href:
        return True
    if "docs.google.com/document" in url.href:
        return True
    if "docs.google.com/spreadsheets" in url.href:
        return True

    return False


def download_doc_as_pdf(url: Url):
    pattern = r'(https://docs\.google\.com/(presentation|document|spreadsheets)/d/[\w-]+)'
    match = re.match(pattern, url.href)
    if not match:
        raise GoogleDocsException(f"Failed to match url: {url.href}")

    base_url = match.group(1)
    export_url = f"{base_url}/export?format=pdf"
    log().debug(f"downloading doc using export url {export_url}")
    return pdf.download_content(Url(href=export_url))
