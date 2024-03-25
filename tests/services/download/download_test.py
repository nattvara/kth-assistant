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
    assert url.content.text == '<p>some text</p>'
