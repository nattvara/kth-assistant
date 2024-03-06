"""
The purpose of this example is to show how to generate text from a huggingface model using
the text generation apis in this repository.
"""

import asyncio

from text.generate import load_hf_model, generate_text_streaming
from text.config import Params
import sys


async def main():
    model = 'mistralai/Mistral-7B-Instruct-v0.2'
    device = 'mps'

    model, tokenizer = load_hf_model(model, device)

    params = Params()
    prompt = 'recite the first page of Moby-Dick'

    async for token in generate_text_streaming(model, tokenizer, device, params, prompt):
        print(token, end='')
        sys.stdout.flush()


if __name__ == '__main__':
    asyncio.run(main())
