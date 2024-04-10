from services.index.index import IndexService
from config.logger import log
from db.models import Url

# 20 minute timeout
TIMEOUT = 20 * 60


async def job(url: Url):
    log().info(f"indexing url: {url.href}")
    try:
        url.refresh()
        url.state = Url.States.INDEXING
        url.save()

        index_service = IndexService()
        await index_service.index_url(url)

        log().info(f"finished indexing url: {url.href}")
    except Exception:  # noqa
        log().error(f"failed indexing url: {url.href}", exc_info=True)
