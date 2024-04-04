from unittest.mock import AsyncMock

import pytest

from services.llm.supported_models import LLMModel, EMBEDDING_MODELS
from services.index.index import IndexService
from db.models import Url, PromptHandle


@pytest.mark.asyncio
async def test_service_checks_if_index_exist_when_adding_url(new_snapshot, mocker):
    mocker.patch('services.index.opensearch.get_client')
    mock_index_exists = mocker.patch('services.index.opensearch.index_exists', return_value=True)
    mocker.patch('services.llm.llm.LLMService.wait_for_handle')

    url = new_snapshot.add_url_with_content()

    index_service = IndexService()

    await index_service.index_url(url)

    mock_index_exists.assert_called_once()


@pytest.mark.asyncio
async def test_service_creates_index_if_not_exists(new_snapshot, mocker):
    mocker.patch('services.index.opensearch.get_client')
    mock_index_exists = mocker.patch('services.index.opensearch.index_exists', return_value=False)
    mock_create_index = mocker.patch('services.index.opensearch.create_index')
    mocker.patch('services.llm.llm.LLMService.wait_for_handle')

    url = new_snapshot.add_url_with_content()

    index_service = IndexService()

    await index_service.index_url(url)

    mock_index_exists.assert_called_once()
    mock_create_index.assert_called_once()


@pytest.mark.asyncio
async def test_service_can_index_url(new_snapshot, mocker):
    handle = PromptHandle(
        prompt="a very long doc",
        llm_model_name=LLMModel.SALESFORCE_SFR_EMBEDDING_MISTRAL,
        embedding=[0.1, 0.2, 0.3]
    )
    handle.save()

    mocker.patch('services.index.opensearch.get_client', return_value=None)
    mocker.patch('services.index.opensearch.index_exists', return_value=False)
    mocker.patch('services.index.opensearch.create_index')
    mocker.patch('services.llm.llm.LLMService.wait_for_handle', AsyncMock(return_value=handle))

    mock_index_document = mocker.patch('services.index.opensearch.index_document')

    url = new_snapshot.add_url_with_content()

    index_service = IndexService()

    await index_service.index_url(url)

    mock_index_document.assert_called_once_with(index_service.client, url.snapshot, f"{url.id}-0", {
        'name': url.content.name,
        'text': url.content.text,
        'url': url.href,
        EMBEDDING_MODELS[LLMModel.OPENAI_TEXT_EMBEDDING_3_LARGE]: [0.1, 0.2, 0.3],
        EMBEDDING_MODELS[LLMModel.SALESFORCE_SFR_EMBEDDING_MISTRAL]: [0.1, 0.2, 0.3],
    })

    url.refresh()
    assert url.state == Url.States.INDEXED
