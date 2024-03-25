import pytest

from jobs.crawl.start_crawler_worker import job
from db.models import Url


@pytest.mark.asyncio
async def test_start_crawler_worker_will_checkout_url_and_crawl_url(
    get_crawler_service,
    get_download_service,
    new_snapshot,
    mocker,
):
    crawler_service = await get_crawler_service
    download_service = await get_download_service
    mocker.patch("asyncio.sleep")
    mocker.patch("jobs.crawl.start_crawler_worker.get_crawler_service", return_value=crawler_service.service)
    mocker.patch("jobs.crawl.start_crawler_worker.get_download_service", return_value=download_service.service)
    mocker.patch("services.crawler.content_extraction.get_all_links_from_page", return_value=[])

    url = new_snapshot.add_unvisited_url()

    await job()

    url.refresh()
    assert url.state == Url.States.VISITED


@pytest.mark.asyncio
async def test_start_crawler_enqueues_itself_the_next_minute(
    get_crawler_service,
    get_download_service,
    new_snapshot,
    mocker
):
    crawler_service = await get_crawler_service
    download_service = await get_download_service
    mocker.patch("asyncio.sleep")
    mocker.patch("jobs.crawl.start_crawler_worker.get_crawler_service", return_value=crawler_service.service)
    mocker.patch("jobs.crawl.start_crawler_worker.get_download_service", return_value=download_service.service)
    mock_start_job_again_in = mocker.patch(
        "jobs.crawl.start_crawler_worker.start_job_again_in",
    )

    new_snapshot.add_unvisited_url()

    await job()

    mock_start_job_again_in.assert_called_once_with(60)
