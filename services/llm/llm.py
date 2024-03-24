from typing import Optional

from redis.asyncio import Redis

from db.actions.prompt_handles import find_most_recent_pending_handle_for_model
from services.llm.supported_models import LLMModel
from db.models import PromptHandle
from llms.config import Params
import cache.mutex as mutex


class NoPendingPromptHandleError(Exception):
    pass


class LLMService:

    def __init__(self, model: LLMModel, redis: Redis):
        self.model = model
        self.redis = redis

    @staticmethod
    def dispatch_prompt(prompt: str, model_name: LLMModel, model_params: Optional[Params] = None) -> PromptHandle:
        handle = PromptHandle(prompt=prompt, model_name=model_name, model_params=model_params)
        handle.save()
        return handle

    async def checkout(self) -> PromptHandle:
        handle = self.next()

        lock_name = f'prompt_handle_{handle.id}'
        await mutex.acquire_lock(self.redis, lock_name)

        try:
            handle.state = PromptHandle.States.IN_PROGRESS
            handle.save()
        finally:
            await mutex.release_lock(self.redis, lock_name)

        return handle

    def next(self) -> PromptHandle:
        handle = find_most_recent_pending_handle_for_model(self.model)
        if handle is None:
            raise NoPendingPromptHandleError("no pending handles was found")
        return handle

    def has_next(self) -> bool:
        handle = find_most_recent_pending_handle_for_model(self.model)
        return handle is not None
