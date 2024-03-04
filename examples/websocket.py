import asyncio
import websockets

from services.llm import LLMService


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
