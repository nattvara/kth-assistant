from unittest.mock import call

from services.llm import LLMService, Worker


def test_worker_will_poll_the_llm_service_every_50_milliseconds_for_next_handle(mocker):
    service_mock = mocker.Mock(spec=LLMService)
    has_next_side_effects = [False, False, False, True]
    service_mock.has_next.side_effect = lambda: has_next_side_effects.pop(0) if has_next_side_effects else False

    worker = Worker(service=service_mock)

    sleep_mock = mocker.patch('time.sleep', side_effect=lambda _: worker.stop() if not has_next_side_effects else None)

    worker.run()

    sleep_mock.assert_any_call(0.05)
    expected_calls = [call(0.05) for _ in range(sleep_mock.call_count)]
    sleep_mock.assert_has_calls(expected_calls, any_order=False)

    # This should have been called once as the side effects specify the last call being true
    service_mock.checkout.assert_called_once()
