from db.actions.prompt_handles import find_most_recent_pending_handle
from db.models import PromptHandle


class NoPendingPromptHandleError(Exception):
    pass


class LLMService:

    def __init__(self):
        pass

    def dispatch_prompt(self, prompt: str) -> PromptHandle:
        handle = PromptHandle(prompt=prompt)
        handle.save()
        return handle

    def checkout(self) -> PromptHandle:
        handle = self.next()
        handle.state = PromptHandle.States.IN_PROGRESS
        handle.save()
        return handle

    def next(self) -> PromptHandle:
        handle = find_most_recent_pending_handle()
        if handle is None:
            raise NoPendingPromptHandleError("no pending handles was found")
        return handle

    def has_next(self) -> bool:
        handle = find_most_recent_pending_handle()
        return handle is not None
