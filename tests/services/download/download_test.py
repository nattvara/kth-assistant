from unittest.mock import AsyncMock

import pytest

from services.download.download import InvalidUrlStateException


@pytest.mark.asyncio
async def test_download_service_throws_exception_if_trying_to_save_content_from_unvisited_url(
    get_download_service,
    new_snapshot
):
    download_service = await get_download_service

    url = new_snapshot.add_unvisited_url()

    with pytest.raises(InvalidUrlStateException):
        await download_service.service.save_url_content(url)


@pytest.mark.asyncio
async def test_download_service_can_download_content_from_canvas_url(mocker, get_download_service, new_snapshot):
    mocker.patch("services.download.canvas.download_content", AsyncMock(return_value='<p>some text</p>'))
    download_service = await get_download_service

    url = new_snapshot.add_visited_url()
    url.href = 'https://canvas.kth.se/foo'
    url.save()

    await download_service.service.save_url_content(url)

    url.refresh()

    assert url.content is not None
    assert url.content.text == 'some text'


@pytest.mark.asyncio
async def test_download_service_can_download_content_from_non_canvas_url(mocker, get_download_service, new_snapshot):
    mocker.patch("services.download.web.download_content", AsyncMock(return_value='<p>some example text</p>'))
    download_service = await get_download_service

    url = new_snapshot.add_visited_url()
    url.href = 'https://example.com/'
    url.save()

    await download_service.service.save_url_content(url)

    url.refresh()

    assert url.content is not None
    assert url.content.text == 'some example text'


@pytest.mark.asyncio
async def test_download_service_can_download_content_from_pdf_urls(mocker, get_download_service, new_snapshot):
    mocker.patch("services.download.pdf.download_content", return_value=('/tmp/file.pdf', 'somefile.pdf'))
    mocker.patch("pdfminer.high_level.extract_text", return_value="pdf content...")
    download_service = await get_download_service

    url = new_snapshot.add_visited_url()
    url.is_download = True
    url.save()

    await download_service.service.save_url_content(url)

    url.refresh()

    assert url.content is not None
    assert url.content.text == 'pdf content...'
    assert url.content.name == 'somefile.pdf'
