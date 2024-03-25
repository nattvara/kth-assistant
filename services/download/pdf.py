from urllib.parse import unquote
import tempfile

import requests

from db.actions.cookie import find_cookie_by_identifier
import config.settings as settings
from config.logger import log
from db.models import Url


class DownloadPdfException(Exception):
    pass


def create_temp_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False, dir='/tmp')
    try:
        return temp_file.name
    finally:
        temp_file.close()


def download_content(url: Url) -> (str, str):
    cookie = find_cookie_by_identifier(settings.get_settings().COOKIE_IDENTIFIER)
    if cookie is None:
        raise DownloadPdfException(f"could not find any cookie"
                                        f"with identifier: {settings.get_settings().COOKIE_IDENTIFIER}")

    cookies_string = cookie.value.strip()
    cookies = requests.utils.cookiejar_from_dict({c.split('=')[0]: c.split('=')[1] for c in cookies_string.split('; ')})

    response = requests.get(url.href, cookies=cookies, stream=True) if cookies else requests.get(url.href, stream=True)

    if not response.status_code == 200:
        raise DownloadPdfException(f"Failed to download file. Status code: {response.status_code}")

    content_disposition = response.headers.get('content-disposition')
    if content_disposition:
        filename = unquote(content_disposition.split('filename=')[-1].strip('"'))
    else:
        filename = url.href.split('/')[-1]

    unique_filename = create_temp_file()

    with open(unique_filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    if cookies:
        log().info(f"File downloaded successfully (with cookie file): {unique_filename}")
    else:
        log().info(f"File downloaded successfully: {unique_filename}")

    return unique_filename, filename
