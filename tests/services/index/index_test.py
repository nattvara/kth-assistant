from services.index.index import IndexService
from db.models import Url


def test_service_checks_if_index_exist_when_adding_url(new_snapshot, mocker):
    mocker.patch('services.index.opensearch.get_client')
    mock_index_exists = mocker.patch('services.index.opensearch.index_exists', return_value=True)

    url = new_snapshot.add_url_with_content()

    index_service = IndexService()

    index_service.index_url(url)

    mock_index_exists.assert_called_once()


def test_service_creates_index_if_not_exists(new_snapshot, mocker):
    mocker.patch('services.index.opensearch.get_client')
    mock_index_exists = mocker.patch('services.index.opensearch.index_exists', return_value=False)
    mock_create_index = mocker.patch('services.index.opensearch.create_index')

    url = new_snapshot.add_url_with_content()

    index_service = IndexService()

    index_service.index_url(url)

    mock_index_exists.assert_called_once()
    mock_create_index.assert_called_once()


def test_service_can_index_url(new_snapshot, mocker):
    mocker.patch('services.index.opensearch.get_client', return_value=None)
    mocker.patch('services.index.opensearch.index_exists', return_value=False)
    mocker.patch('services.index.opensearch.create_index')
    mock_index_document = mocker.patch('services.index.opensearch.index_document')

    url = new_snapshot.add_url_with_content()

    index_service = IndexService()

    index_service.index_url(url)

    mock_index_document.assert_called_once_with(index_service.client, url.snapshot, f"{url.id}-0", {
        'name': url.content.name,
        'text': url.content.text,
        'url': url.href,
    })

    url.refresh()
    assert url.state == Url.States.INDEXED
