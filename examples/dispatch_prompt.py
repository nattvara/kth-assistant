"""
The purpose of this example is to dispatch a prompt and wait for the
response to be streamed back by a worker over the websocket of the
prompt handle.

NOTE: this example needs a redis and postgres server to be running

$ docker run --name some-postgres -e POSTGRES_PASSWORD=postgres -d -p 5432:5432 postgres
$ docker run -p 6379:6379 -it redis/redis-stack:latest

Also needs at least one worker to be running:

$ llm_worker MISTRAL_7B_INSTRUCT
"""


import websockets
import asyncio
import sys

from beeprint import pp

from services.llm.worker import TERMINATION_STRING
from services.llm.supported_models import LLMModel
from services.llm.llm import LLMService
import config.settings as settings


async def main():
    prompt = "recite the first page of moby dick"
    handle = LLMService.dispatch_prompt(prompt, LLMModel.GOOGLE_GEMMA_7B)

    pp(handle)

    websocket_url = f"ws://{settings.get_settings().HOST}:{settings.get_settings().PORT}{handle.websocket_uri}"
    async with websockets.connect(websocket_url) as ws_requester:
        while True:
            response = await ws_requester.recv()
            if response == TERMINATION_STRING:
                await ws_requester.close()
                break
            print(response, end='')
            sys.stdout.flush()


if __name__ == '__main__':
    asyncio.run(main())
