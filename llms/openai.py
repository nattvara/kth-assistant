from typing import Tuple, AsyncGenerator, List

from openai import AsyncOpenAI

from config.settings import get_settings
from llms.config import Params
from config.logger import log

MODEL = 'gpt-4'
EMBEDDING_MODEL = 'text-embedding-3-large'


class OpenAiError(Exception):
    pass


def load_openai_sdk(model_name: str, device: str) -> Tuple[AsyncOpenAI, None]:
    api_key = get_settings().OPENAI_API_KEY
    if api_key is None:
        raise OpenAiError("OpenAI API key was not set in the settings.")
    client = AsyncOpenAI(api_key=api_key)
    return client, None


async def generate_text_streaming(
    model: AsyncOpenAI,
    tokenizer,
    device,
    params: Params,
    prompt: str,
) -> AsyncGenerator[str, None]:
    """
    A wrapper function around the stream_tokens_async function
    to match the signature of the generate_text_streaming function
    used for models from huggingface.
    """
    async for token in stream_tokens_async(model, params, prompt):
        yield token


async def stream_tokens_async(
    client: AsyncOpenAI,
    params: Params,
    prompt: str,
) -> AsyncGenerator[str, None]:
    stream = await client.chat.completions.create(
        model=MODEL,
        temperature=params.temperature,
        max_tokens=params.max_new_tokens,
        messages=[
            {'role': 'system', 'content': params.system_prompt},
            {'role': 'user', 'content': prompt},
        ],
        stream=True,
    )
    async for chunk in stream:
        token = chunk.choices[0].delta.content or ''
        yield token


async def compute_embedding(model: AsyncOpenAI, tokeniser, text: str) -> List[float]:
    log().info(f"Computing embedding using openai embedding model: {EMBEDDING_MODEL}")
    response = await model.embeddings.create(input=text, model=EMBEDDING_MODEL)
    log().info(f"Usage was {response.usage}")
    return response.data[0].embedding
