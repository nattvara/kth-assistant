from unittest.mock import call

import pytest

from services.llm import LLMService, Worker, TERMINATION_STRING
import config.settings as settings
from db.models import PromptHandle


@pytest.fixture
def create_worker(mock_load_hf_model, create_mock_generate_text_streaming):
    def create_worker_func(service, mock_tokens, return_mock_generate_text=False):
        mock_generate_text = create_mock_generate_text_streaming(mock_tokens)
        worker = Worker(
            llm_service=service,
            model_name='some_org/some_model',
            device='cuda',
            model_loader_func=mock_load_hf_model,
            text_generator=mock_generate_text
        )
        if return_mock_generate_text:
            return worker, mock_generate_text
        return worker

    return create_worker_func


@pytest.mark.asyncio
async def test_worker_will_poll_the_llm_service_every_50_milliseconds_for_next_handle(mocker, create_worker, create_websocket_mocks):
    create_websocket_mocks()
    mock_tokens = ['some', ' ', 'tokens']

    service_mock = mocker.Mock(spec=LLMService)
    has_next_side_effects = [False, False, False, True]
    service_mock.has_next.side_effect = lambda: has_next_side_effects.pop(0) if has_next_side_effects else False

    sleep_mock = mocker.patch('asyncio.sleep', side_effect=lambda _: worker.stop() if not has_next_side_effects else None)

    worker = create_worker(service_mock, mock_tokens)
    await worker.run()

    sleep_mock.assert_any_call(0.05)
    expected_calls = [call(0.05) for _ in range(sleep_mock.call_count)]
    sleep_mock.assert_has_calls(expected_calls, any_order=False)

    # This should have been called once as the side effects specify the last call being true
    service_mock.checkout.assert_called_once()


@pytest.mark.asyncio
async def test_worker_generates_text_from_the_handles_prompt(create_worker, create_websocket_mocks):
    create_websocket_mocks()

    mock_tokens = ['baby', ' ', 'don', '\'', 't', ' ', 'hurt', ' ', 'me']

    service = LLMService()
    handle = PromptHandle(service=service, prompt="what is love?")
    handle.save()

    worker, mock_generate_text = create_worker(service, mock_tokens, True)
    await worker.process_prompt_handle(handle)

    mock_generate_text.assert_called_once()
    called_args, _ = mock_generate_text.call_args
    assert called_args[4] == handle.prompt, "generate_text was not called with the correct prompt"


@pytest.mark.asyncio
async def test_worker_connects_to_the_websocket_of_the_handle(create_worker, create_websocket_mocks):
    _, mock_connect = create_websocket_mocks()
    mock_tokens = ['baby', ' ', 'don', '\'', 't', ' ', 'hurt', ' ', 'me']

    service = LLMService()
    handle = PromptHandle(service=service, prompt="what is love?")
    handle.save()

    worker, mock_generate_text = create_worker(service, mock_tokens, True)
    await worker.process_prompt_handle(handle)

    websocket_url = f"ws://{settings.get_settings().HOST}:{settings.get_settings().PORT}{handle.websocket_uri}"
    mock_connect.assert_called_once_with(websocket_url)


@pytest.mark.asyncio
async def test_worker_sends_all_generated_tokens_to_the_websocket_with_end_token(create_worker, create_websocket_mocks):
    mock_ws, mock_connect = create_websocket_mocks()
    mock_tokens = ['baby', ' ', 'don', '\'', 't', ' ', 'hurt', ' ', 'me']

    service = LLMService()
    handle = PromptHandle(service=service, prompt="what is love?")
    handle.save()

    worker, mock_generate_text = create_worker(service, mock_tokens, True)
    await worker.process_prompt_handle(handle)

    websocket_url = f"ws://{settings.get_settings().HOST}:{settings.get_settings().PORT}{handle.websocket_uri}"
    mock_connect.assert_called_once_with(websocket_url)

    assert mock_ws.send.call_count == len(mock_tokens) + 1

    for token in mock_tokens:
        mock_ws.send.assert_any_call(token)

    mock_ws.send.assert_any_call(TERMINATION_STRING)


@pytest.mark.asyncio
async def test_worker_saves_entire_response_when_finished(create_worker, create_websocket_mocks):
    create_websocket_mocks()
    mock_tokens = ['baby', ' ', 'don', '\'', 't', ' ', 'hurt', ' ', 'me']

    service = LLMService()
    handle = PromptHandle(service=service, prompt="what is love?")
    handle.save()

    worker, mock_generate_text = create_worker(service, mock_tokens, True)
    await worker.process_prompt_handle(handle)

    handle.refresh()
    assert handle.response == "baby don't hurt me"
