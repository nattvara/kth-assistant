from typing import List

from llms.openai import get_tokeniser


def split_text_with_overlap(text: str, chunk_size: int = 1800, overlap: int = 100) -> List[str]:
    # using the openai tokeniser which won't be the same for all models, but for this case
    # the particular tokeniser doesn't matter. And it's the easiest and fastest to load
    tokeniser = get_tokeniser()

    tokens = tokeniser.encode(text)
    chunks = []
    start_index = 0
    tokens_length = len(tokens)

    while start_index < tokens_length:
        if start_index > 0:
            start_index -= overlap

        end_index = min(start_index + chunk_size, tokens_length)
        chunk_tokens = tokens[start_index:end_index]
        chunks.append(tokeniser.decode(chunk_tokens))

        start_index = end_index

    return chunks
