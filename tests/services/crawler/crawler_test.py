from unittest.mock import AsyncMock

import pytest
import arrow

from services.crawler.crawler import CrawlerService, NoUnvisitedUrlException, NoValidSnapshotException
from db.models import Snapshot, Url


def test_crawler_can_create_snapshot_of_course(valid_course):
    CrawlerService.create_snapshot(valid_course)

    assert Snapshot.select().filter(Snapshot.course == valid_course.id).exists()


def test_creating_new_snapshot_also_creates_the_root_url(valid_course):
    snapshot = CrawlerService.create_snapshot(valid_course)

    assert Url.select().filter(Url.snapshot == snapshot.id).exists()
    assert len(snapshot.urls) == 1


def test_the_current_snapshot_is_always_the_most_recent_snapshot_without_any_unvisited_urls(mocker, valid_course):
    mocked_time = arrow.get('2024-03-24T00:00:00Z')

    with mocker.patch('arrow.now', return_value=mocked_time):
        snapshot_1 = CrawlerService.create_snapshot(valid_course)
        snapshot_1.created_at = arrow.now().shift(hours=-2)
        snapshot_1.save()
        snapshot_2 = CrawlerService.create_snapshot(valid_course)
        snapshot_2.created_at = arrow.now().shift(hours=-1)
        snapshot_2.save()
        snapshot_3 = CrawlerService.create_snapshot(valid_course)

        # at this point no snapshot is valid since all the three above have unvisited urls (the root url)
        with pytest.raises(NoValidSnapshotException):
            CrawlerService.current_snapshot(valid_course)

        url = snapshot_1.urls[0]
        url.state = Url.States.VISITED
        url.save()

        assert CrawlerService.current_snapshot(valid_course) == snapshot_1

        url = snapshot_2.urls[0]
        url.state = Url.States.VISITED
        url.save()

        assert CrawlerService.current_snapshot(valid_course) == snapshot_2

        # adding a new url to snapshot_2 would mean snapshot one becomes valid again
        url = Url(snapshot=snapshot_2, href=f"https://example.com/1")
        url.save()

        assert CrawlerService.current_snapshot(valid_course) == snapshot_1

        url = snapshot_3.urls[0]
        url.state = Url.States.VISITED
        url.save()

        assert CrawlerService.current_snapshot(valid_course) == snapshot_3


@pytest.mark.asyncio
async def test_next_url_from_service_is_the_most_recent_url(get_crawler_service, new_snapshot):
    crawler_service = await get_crawler_service

    url_1 = Url(snapshot=new_snapshot.snapshot, href=f"https://example.com/1")
    url_2 = Url(snapshot=new_snapshot.snapshot, href=f"https://example.com/2")
    url_3 = Url(snapshot=new_snapshot.snapshot, href=f"https://example.com/3")
    url_1.save()
    url_2.save()
    url_3.save()

    url = crawler_service.service.next()

    assert url.id == url_1.id


@pytest.mark.asyncio
async def test_next_url_from_service_is_always_in_unvisited_state(get_crawler_service, new_snapshot):
    crawler_service = await get_crawler_service

    url_1 = Url(snapshot=new_snapshot.snapshot, href=f"https://example.com/1")
    url_2 = Url(snapshot=new_snapshot.snapshot, href=f"https://example.com/2")
    url_3 = Url(snapshot=new_snapshot.snapshot, href=f"https://example.com/3")
    url_1.save()
    url_2.save()
    url_3.save()

    url_1.state = Url.States.VISITED
    url_1.save()

    url = crawler_service.service.next()

    assert url.id == url_2.id


@pytest.mark.asyncio
async def test_has_next_returns_true_only_if_any_unvisited_url_exist(get_crawler_service, new_snapshot):
    crawler_service = await get_crawler_service

    url_1 = Url(snapshot=new_snapshot.snapshot, href=f"https://example.com/1")
    url_2 = Url(snapshot=new_snapshot.snapshot, href=f"https://example.com/2")
    url_3 = Url(snapshot=new_snapshot.snapshot, href=f"https://example.com/3")
    url_1.save()
    url_2.save()
    url_3.save()

    assert crawler_service.service.has_next()

    url_1.state = Url.States.VISITED
    url_1.save()

    assert crawler_service.service.has_next()

    url_2.state = Url.States.VISITED
    url_2.save()

    assert crawler_service.service.has_next()

    url_3.state = Url.States.VISITED
    url_3.save()

    assert not crawler_service.service.has_next()


@pytest.mark.asyncio
async def test_next_throws_exception_if_no_unvisited_url_exists(get_crawler_service):
    crawler_service = await get_crawler_service

    with pytest.raises(NoUnvisitedUrlException):
        crawler_service.service.next()


@pytest.mark.asyncio
async def test_checkout_returns_a_url_and_updates_its_state(get_crawler_service, new_snapshot):
    crawler_service = await get_crawler_service

    url_1 = Url(snapshot=new_snapshot.snapshot, href=f"https://example.com/1")
    url_1.save()

    url = await crawler_service.service.checkout()

    assert url.id == url_1.id
    assert url.state == url_1.States.CRAWLING


@pytest.mark.asyncio
async def test_checkout_acquires_a_redis_lock_on_url(mocker, get_crawler_service, new_snapshot):
    crawler_service = await get_crawler_service

    mock_acquire_lock = mocker.patch('cache.mutex.acquire_lock', new_callable=AsyncMock)
    mock_release_lock = mocker.patch('cache.mutex.release_lock', new_callable=AsyncMock)

    url = Url(snapshot=new_snapshot.snapshot, href=f"https://example.com/1")
    url.save()

    await crawler_service.service.checkout()

    mock_acquire_lock.assert_awaited_once_with(crawler_service.redis_conn, f'url_{url.id}')
    mock_release_lock.assert_awaited_once_with(crawler_service.redis_conn, f'url_{url.id}')


@pytest.mark.asyncio
async def test_crawler_service_can_visit_a_url(get_crawler_service, new_snapshot):
    crawler_service = await get_crawler_service

    url = new_snapshot.add_unvisited_url()

    await crawler_service.service.crawl_url(url)
    url.refresh()

    assert url.state == Url.States.VISITED
    crawler_service.playwright.page.goto.assert_awaited_once_with(url.href, wait_until='load')
    crawler_service.playwright.page.wait_for_load_state.assert_awaited_once_with('load')
