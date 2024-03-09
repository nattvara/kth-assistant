import pytest

from services.llm.llm import NoPendingPromptHandleError, LLMService
from services.llm.supported_models import LLMModel
from db.models import PromptHandle
from llms.config import Params


def test_llm_service_can_dispatch_a_prompt_and_return_handle(llm_model_name):
    prompt = "who is the most iconic fashion icon of the 20th century?"

    handle = LLMService.dispatch_prompt(prompt, llm_model_name)

    assert isinstance(handle, PromptHandle)
    assert handle.state == PromptHandle.States.PENDING
    assert handle.prompt == prompt


def test_next_handle_from_service_is_the_most_recent_handle(llm_prompt, llm_model_name):
    service = LLMService(llm_model_name)

    handle_1 = PromptHandle(prompt=llm_prompt, model_name=llm_model_name)
    handle_2 = PromptHandle(prompt=llm_prompt, model_name=llm_model_name)
    handle_3 = PromptHandle(prompt=llm_prompt, model_name=llm_model_name)
    handle_1.save()
    handle_2.save()
    handle_3.save()

    handle = service.next()

    assert handle.id == handle_1.id


def test_next_handle_from_service_is_always_in_pending_state(llm_prompt, llm_model_name):
    service = LLMService(llm_model_name)

    handle_1 = PromptHandle(prompt=llm_prompt, model_name=llm_model_name)
    handle_2 = PromptHandle(prompt=llm_prompt, model_name=llm_model_name)
    handle_3 = PromptHandle(prompt=llm_prompt, model_name=llm_model_name)
    handle_1.save()
    handle_2.save()
    handle_3.save()

    handle_1.state = PromptHandle.States.FINISHED
    handle_1.save()

    handle = service.next()

    assert handle.id == handle_2.id


def test_has_next_returns_true_only_if_any_pending_handles_exist(llm_prompt, llm_model_name):
    service = LLMService(llm_model_name)

    handle_1 = PromptHandle(prompt=llm_prompt, model_name=llm_model_name)
    handle_2 = PromptHandle(prompt=llm_prompt, model_name=llm_model_name)
    handle_3 = PromptHandle(prompt=llm_prompt, model_name=llm_model_name)
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


def test_next_returns_handles_matching_model_name(llm_prompt):
    model_1 = LLMModel.MISTRAL_7B_INSTRUCT
    model_2 = LLMModel.GOOGLE_GEMMA_7B

    service = LLMService(model_1)

    handle_1 = PromptHandle(prompt=llm_prompt, model_name=model_1)
    handle_2 = PromptHandle(prompt=llm_prompt, model_name=model_2)
    handle_3 = PromptHandle(prompt=llm_prompt, model_name=model_1)
    handle_1.save()
    handle_2.save()
    handle_3.save()

    handle = service.checkout()
    assert handle.id == handle_1.id

    handle = service.checkout()
    assert handle.id == handle_3.id


def test_next_throws_exception_if_no_pending_handle_exists(llm_model_name):
    service = LLMService(llm_model_name)

    with pytest.raises(NoPendingPromptHandleError):
        service.next()


def test_checkout_returns_a_handle_and_updates_its_state(llm_prompt, llm_model_name):
    service = LLMService(llm_model_name)

    handle_1 = PromptHandle(prompt=llm_prompt, model_name=llm_model_name)
    handle_1.save()

    handle = service.checkout()

    assert handle.id == handle_1.id
    assert handle.state == PromptHandle.States.IN_PROGRESS


def test_model_params_can_be_specified(llm_model_name):
    prompt = "what's the slogan of nike?"

    params = Params(
        temperature=0.1,
        max_new_tokens=123,
        context_length=456,
        enable_top_k_filter=False,
        top_k_limit=42,
        enable_top_p_filter=False,
        top_p_threshold=0.42,
        stop_strings=["foo"],
        system_prompt="bar",
    )

    handle_id = LLMService.dispatch_prompt(prompt, llm_model_name, model_params=params).id
    handle = PromptHandle.get(handle_id)

    assert handle.model_params.temperature == 0.1
    assert handle.model_params.max_new_tokens == 123
    assert handle.model_params.context_length == 456
    assert handle.model_params.enable_top_k_filter == False
    assert handle.model_params.top_k_limit == 42
    assert handle.model_params.enable_top_p_filter == False
    assert handle.model_params.top_p_threshold == 0.42
    assert handle.model_params.stop_strings == ["foo"]
    assert handle.model_params.system_prompt == "bar"


def test_model_params_can_be_specified():
    prompt = "tell me a joke"
    model_name = LLMModel.MISTRAL_7B_INSTRUCT

    handle_id = LLMService.dispatch_prompt(prompt, model_name).id
    handle = PromptHandle.get(handle_id)

    assert handle.model_name == model_name
