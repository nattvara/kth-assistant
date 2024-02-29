from db.models import PromptHandle
from services.llm import LLMService


def test_llm_service_can_dispatch_a_prompt_and_return_handle():
    service = LLMService()
    prompt = "who is the most iconic fashion icon of the 20th century?"

    handle = service.dispatch_prompt(prompt)

    assert isinstance(handle, PromptHandle)
    assert handle.state == PromptHandle.States.PENDING
    assert handle.prompt == prompt
