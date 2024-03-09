"""
The purpose of this example is how to create a prompt handle, and very simply
demonstrate how the websocket connection is setup. This example shows
a worker sending a message that will be received by a requester.

NOTE: this example needs a redis and postgres server to be running

$ docker run --name some-postgres -e POSTGRES_PASSWORD=postgres -d -p 5432:5432 postgres
$ docker run -p 6379:6379 -it redis/redis-stack:latest

"""

import asyncio
import websockets

from services.llm.supported_models import LLMModel
from db.models import PromptHandle


async def main():
    try:
        llm = LLMService()
        prompt = "recite the first page of moby dick"
        handle = llm.dispatch_prompt(prompt)

        print(handle)

        worker_ws_uri = 'ws://localhost:8000' + handle.websocket_uri
        requester_ws_uri = 'ws://localhost:8000' + handle.websocket_uri

        async with websockets.connect(worker_ws_uri) as ws_worker:
            async with websockets.connect(requester_ws_uri) as ws_requester:
                await ws_worker.send("ping from worker")
                response = await ws_requester.recv()
                print('Requester received: ' + response)
                await ws_requester.close()

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    asyncio.run(main())
