from typing import Tuple, AsyncGenerator, List

from openai import AsyncOpenAI
import tiktoken
from tiktoken import Encoding

from config.settings import get_settings
from llms.config import Params
from config.logger import log

MODEL = 'gpt-4-turbo'
EMBEDDING_MODEL = 'text-embedding-3-large'
MAX_TOKENS = 4096


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
    encoding = tiktoken.encoding_for_model(MODEL)
    num_tokens = len(encoding.encode(prompt))
    num_tokens -= len(encoding.encode(params.system_prompt))

    max_tokens = MAX_TOKENS
    if params.max_new_tokens < MAX_TOKENS:
        max_tokens = params.max_new_tokens

    log().debug(f"init openai stream. MAX_TOKENS: {MAX_TOKENS}, prompt_tokens: {num_tokens}, params.max_new_tokens: "
                f"{params.max_new_tokens}, max_tokens being used: {max_tokens}")

    stream = await client.chat.completions.create(
        model=MODEL,
        temperature=params.temperature,
        max_tokens=max_tokens,
        messages=[
            {'role': 'system', 'content': params.system_prompt},
            {'role': 'user', 'content': prompt},
        ],
        stream=True,
    )
    async for chunk in stream:
        token = chunk.choices[0].delta.content or ''
        if token in params.stop_strings:
            break
        yield token


async def compute_embedding(model: AsyncOpenAI, tokeniser, text: str) -> List[float]:
    log().info(f"Computing embedding using openai embedding model: {EMBEDDING_MODEL}")
    response = await model.embeddings.create(input=text, model=EMBEDDING_MODEL)
    log().info(f"Usage was {response.usage}")
    return response.data[0].embedding


def truncate_text_to_token_limit(input_string: str, token_limit: int) -> str:
    encoding = tiktoken.encoding_for_model(MODEL)
    tokens = encoding.encode(input_string)

    if len(tokens) > token_limit:
        truncated_tokens = tokens[:token_limit]
        return encoding.decode(truncated_tokens)
    else:
        return input_string


def get_tokeniser() -> Encoding:
    encoding = tiktoken.encoding_for_model(MODEL)
    return encoding
