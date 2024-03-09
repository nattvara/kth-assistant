from typing import Optional

from db.actions.prompt_handles import find_most_recent_pending_handle_for_model
from services.llm.supported_models import LLMModel
from db.models import PromptHandle
from llms.config import Params


class NoPendingPromptHandleError(Exception):
    pass


class LLMService:

    def __init__(self, model: LLMModel):
        self.model = model

    @staticmethod
    def dispatch_prompt(prompt: str, model_name: LLMModel, model_params: Optional[Params] = None) -> PromptHandle:
        handle = PromptHandle(prompt=prompt, model_name=model_name, model_params=model_params)
        handle.save()
        return handle

    def checkout(self) -> PromptHandle:
        handle = self.next()
        handle.state = PromptHandle.States.IN_PROGRESS
        handle.save()
        return handle

    def next(self) -> PromptHandle:
        handle = find_most_recent_pending_handle_for_model(self.model)
        if handle is None:
            raise NoPendingPromptHandleError("no pending handles was found")
        return handle

    def has_next(self) -> bool:
        handle = find_most_recent_pending_handle_for_model(self.model)
        return handle is not None
