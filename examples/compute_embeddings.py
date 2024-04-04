"""
The purpose of this example is to dispatch a text to compute embeddings for.

NOTE: this example needs a redis and postgres server to be running

$ docker run --name some-postgres -e POSTGRES_PASSWORD=postgres -d -p 5432:5432 postgres
$ docker run -p 6379:6379 -it redis/redis-stack:latest

Also needs at least one worker to be running:

$ llm_worker SALESFORCE_SFR_EMBEDDING_MISTRAL cpu
"""

import asyncio
import json

from services.llm.supported_models import LLMModel
from services.llm.llm import LLMService


async def main():
    prompt = "how many homeworks are there?"
    print(f"generating embedding for \"{prompt}\"")

    handle = LLMService.dispatch_prompt(prompt, LLMModel.SALESFORCE_SFR_EMBEDDING_MISTRAL)
    handle = await LLMService.wait_for_handle(handle)

    print(json.dumps(handle.embedding))


if __name__ == '__main__':
    asyncio.run(main())
