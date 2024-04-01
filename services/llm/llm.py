import asyncio
from typing import Optional
import time

from redis.asyncio import Redis

from db.actions.prompt_handles import find_most_recent_pending_handle_for_model
from services.llm.supported_models import LLMModel
from db.models import PromptHandle
from llms.config import Params
import cache.mutex as mutex


class NoPendingPromptHandleError(Exception):
    pass


class LLMServiceTimeoutException(Exception):
    pass


class LLMService:

    def __init__(self, model: LLMModel, redis: Redis):
        self.model = model
        self.redis = redis

    @staticmethod
    def dispatch_prompt(prompt: str, llm_model_name: LLMModel, llm_model_params: Optional[Params] = None) -> PromptHandle:
        handle = PromptHandle(prompt=prompt, llm_model_name=llm_model_name, llm_model_params=llm_model_params)
        handle.save()
        return handle

    @staticmethod
    async def wait_for_handle(handle: PromptHandle, timeout_seconds: int = 120) -> PromptHandle:
        start_time = time.monotonic()
        while True:
            handle.refresh()
            if handle.state == PromptHandle.States.FINISHED:
                break
            elif time.monotonic() - start_time > timeout_seconds:
                raise LLMServiceTimeoutException(f"Waiting for prompt handle {handle.id} timed out.")
            await asyncio.sleep(0.01)
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
