from websockets import ConnectionClosedOK
from typing import Callable
import websockets
import asyncio

from text.generate import generate_text_streaming, load_hf_model
from db.models import PromptHandle
from services.llm import LLMService
import config.settings as settings
from text.config import Params
from config.logger import log

TERMINATION_STRING = "<<<END_OF_STREAM>>>"


class Worker:

    def __init__(
            self,
            llm_service: LLMService,
            model_name: str,
            device: str,
            model_loader_func: Callable = load_hf_model,
            text_generator: Callable = generate_text_streaming,
    ):
        self.service = llm_service
        self.running = False
        self.model_name = model_name
        self.device = device
        self.text_generator = text_generator

        log().info(f"Loading model \"{self.model_name}\" onto device \"{self.device}\"")
        self.model, self.tokenizer = model_loader_func(self.model_name, self.device)
        log().info("model loaded, worker is ready")

    async def process_prompt_handle(self, handle):
        log().info(f"Processing handle with id {handle.id} created at {handle.created_at}")
        log().debug(f"The prompt of the handle is: \"{handle.prompt}\"")

        websocket_url = f"ws://{settings.get_settings().HOST}:{settings.get_settings().PORT}{handle.websocket_uri}"

        response = ""

        log().debug(f"connecting to websocket {websocket_url}")
        try:
            async with websockets.connect(websocket_url) as websocket:
                log().debug(f"generating response...")

                params = Params()
                index = 1
                async for token in self.text_generator(self.model, self.tokenizer, self.device, params, handle.prompt):
                    await websocket.send(token)
                    response += token
                    index += 1
                    if index % 50 == 0:
                        log().info(f"Generated {index} tokens...")

                await websocket.send(TERMINATION_STRING)
                await websocket.close()
        except ConnectionClosedOK:
            log().warning(f"Websocket closed by the server, with: ConnectionClosedOK.")

        log().debug(f"Disconnected from the websocket")
        log().debug(f"The complete response was: {response}")

        handle.refresh()
        handle.state = PromptHandle.States.FINISHED
        handle.response = response
        handle.save()

    async def run(self):
        self.running = True
        while self.running:
            try:
                if self.service.has_next():
                    handle = self.service.checkout()
                    await self.process_prompt_handle(handle)
                await asyncio.sleep(0.05)
            except KeyboardInterrupt:
                log().info("Stopping worker...")
                self.stop()

    def stop(self):
        self.running = False


if __name__ == '__main__':
    log().info("Starting worker")
    worker = Worker(llm_service=LLMService(), model_name='mistralai/Mistral-7B-Instruct-v0.2', device='mps')
    asyncio.run(worker.run())
