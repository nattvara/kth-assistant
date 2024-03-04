import pytest

from services.llm import LLMService
from db.models import PromptHandle
from services.llm.llm import NoPendingPromptHandleError


def test_llm_service_can_dispatch_a_prompt_and_return_handle():
    service = LLMService()
    prompt = "who is the most iconic fashion icon of the 20th century?"

    handle = service.dispatch_prompt(prompt)

    assert isinstance(handle, PromptHandle)
    assert handle.state == PromptHandle.States.PENDING
    assert handle.prompt == prompt


def test_next_handle_from_service_is_the_most_recent_handle():
    service = LLMService()

    handle_1 = PromptHandle()
    handle_2 = PromptHandle()
    handle_3 = PromptHandle()
    handle_1.save()
    handle_2.save()
    handle_3.save()

    handle = service.next()

    assert handle.id == handle_1.id


def test_next_handle_from_service_is_always_in_pending_state():
    service = LLMService()

    handle_1 = PromptHandle()
    handle_2 = PromptHandle()
    handle_3 = PromptHandle()
    handle_1.save()
    handle_2.save()
    handle_3.save()

    handle_1.state = PromptHandle.States.FINISHED
    handle_1.save()

    handle = service.next()

    assert handle.id == handle_2.id


def test_has_next_returns_true_only_if_any_pending_handles_exist():
    service = LLMService()

    handle_1 = PromptHandle()
    handle_2 = PromptHandle()
    handle_3 = PromptHandle()
    handle_1.save()
    handle_2.save()
    handle_3.save()

    assert service.has_next()

    handle_1.state = PromptHandle.States.FINISHED
    handle_1.save()

    assert service.has_next()

    handle_2.state = PromptHandle.States.FINISHED
    handle_2.save()

    assert service.has_next()

    handle_3.state = PromptHandle.States.FINISHED
    handle_3.save()

    assert not service.has_next()


def test_next_throws_exception_if_no_pending_handle_exists():
    service = LLMService()

    with pytest.raises(NoPendingPromptHandleError):
        service.next()


def test_checkout_returns_a_handle_and_updates_its_state():
    service = LLMService()

    handle_1 = PromptHandle()
    handle_1.save()

    handle = service.checkout()

    assert handle.id == handle_1.id
    assert handle.state == PromptHandle.States.IN_PROGRESS
