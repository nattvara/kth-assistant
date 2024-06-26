from websockets import ConnectionClosedOK
from typing import Callable
import websockets
import asyncio
import time

import arrow

from services.llm.supported_models import LLMModel, EMBEDDING_MODELS
from services.llm.llm import LLMService, NoPendingPromptHandleError
from llms.generate import generate_text_streaming, load_hf_model
from services.llm.prompts import prepend_system_prompt
from cache.mutex import LockAlreadyAcquiredException
from llms.embeddings import compute_embedding
from db.models import PromptHandle
import config.settings as settings
from llms.config import Params
from config.logger import log

TERMINATION_STRING = "<<<END_OF_STREAM>>>"


def _get_websocket_url(handle: PromptHandle) -> str:
    if settings.get_settings().PORT == 443:
        protocol = "wss://"
    else:
        protocol = "ws://"

    if settings.get_settings().PORT == 80 or settings.get_settings().PORT == 443:
        websocket_url = f"{protocol}{settings.get_settings().HOST}{handle.websocket_uri}"
    else:
        websocket_url = f"{protocol}{settings.get_settings().HOST}:{settings.get_settings().PORT}{handle.websocket_uri}"

    return websocket_url


class Worker:

    def __init__(
            self,
            llm_service: LLMService,
            llm_model_name: LLMModel,
            device: str,
            model_loader_func: Callable = load_hf_model,
            text_generator: Callable = generate_text_streaming,
            embedding_function: Callable = compute_embedding,
    ):
        self.service = llm_service
        self.running = False
        self.llm_model_name = llm_model_name.value
        self.device = device
        self.text_generator = text_generator
        self.embedding_function = embedding_function

        log().info(f"Loading model \"{self.llm_model_name}\" onto device \"{self.device}\"")
        self.model, self.tokenizer = model_loader_func(self.llm_model_name, self.device)
        log().info("model loaded, worker is ready")

    async def process_prompt_handle(self, handle: PromptHandle):
        log().info(f"Processing handle with id {handle.id} created at {handle.created_at}")
        log().debug(f"The prompt of the handle is: \"{handle.prompt}\"")

        current_time = arrow.now()
        wait_time = current_time - handle.created_at
        handle.time_spent_pending_ms = wait_time.total_seconds() * 1000
        handle.save()

        if handle.llm_model_name in EMBEDDING_MODELS:
            return await self._process_embedding_prompt_handle(handle)
        else:
            return await self._process_standard_prompt_handle(handle)

    async def _process_embedding_prompt_handle(self, handle: PromptHandle):
        number_of_tokens = 0

        log().debug("compute embedding...")
        start_time = time.time()

        prompt = handle.prompt
        embedding = await self.embedding_function(self.model, self.tokenizer, prompt)

        end_time = time.time()
        time_taken = end_time - start_time

        log().debug("finished computing embedding.")

        handle.refresh()
        handle.embedding = embedding
        handle.state = PromptHandle.States.FINISHED
        handle.response_length = number_of_tokens
        handle.response_time_taken_s = int(time_taken)
        handle.save()

    async def _process_standard_prompt_handle(self, handle: PromptHandle):
        websocket_url = _get_websocket_url(handle)

        response = ""
        number_of_tokens = 0
        time_taken = None

        log().debug(f"connecting to websocket {websocket_url}")
        try:
            async with websockets.connect(websocket_url) as websocket:
                log().debug("generating response...")

                params = Params()
                if handle.llm_model_params is not None:
                    params = handle.llm_model_params

                prompt = handle.prompt
                if handle.llm_model_name != LLMModel.OPENAI_GPT4:
                    prompt = prepend_system_prompt(params.system_prompt, handle.prompt)

                index = 1
                start_time = time.time()
                found_less_than = False
                found_less_than_and_pipe = False
                async for token in self.text_generator(self.model, self.tokenizer, self.device, params, prompt):
                    # since the model has a tendency to generate <|user|> strings
                    # this check is here to ensure the model doesn't start generating
                    # dangling "<|" tokens at the end of messages
                    if found_less_than:
                        token = f'<{token}'
                        found_less_than = False

                    if found_less_than_and_pipe:
                        token = f'<|{token}'
                        found_less_than_and_pipe = False

                    if token == '<':
                        found_less_than = True
                        continue

                    if token == '<|':
                        found_less_than_and_pipe = True
                        continue

                    await websocket.send(token)

                    response += token
                    index += 1
                    number_of_tokens += 1
                    if index % 50 == 0:
                        log().info(f"Generated {index} tokens...")

                end_time = time.time()
                time_taken = end_time - start_time
                await websocket.send(TERMINATION_STRING)
                await websocket.close()
        except ConnectionClosedOK:
            log().warning("Websocket closed by the server, with: ConnectionClosedOK.")

        log().debug("Disconnected from the websocket")
        log().debug(f"The complete response was: {response}")

        handle.refresh()
        handle.state = PromptHandle.States.FINISHED
        handle.response = response
        handle.response_length = number_of_tokens
        handle.response_time_taken_s = int(time_taken)
        handle.save()

    async def run(self):
        self.running = True
        while self.running:
            try:
                if self.service.has_next():
                    try:
                        handle = await self.service.checkout()
                        await self.process_prompt_handle(handle)
                    except LockAlreadyAcquiredException:
                        log().debug("Found a lock the handle. Skipping for now.")
                    except NoPendingPromptHandleError:
                        log().error("NoPendingPromptHandleError was thrown. is probably caused by a race condition.")
                await asyncio.sleep(0.05)
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        log().info("Stopping worker...")
        self.running = False
