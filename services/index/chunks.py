from typing import List


def split_text_with_overlap(text, chunk_size=7500, overlap=100) -> List[str]:
    if overlap >= chunk_size:
        raise ValueError('Overlap must be less than the chunk size.')

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        if start > 0:
            start -= overlap

        end = min(start + chunk_size, text_length)

        chunks.append(text[start:end])

        start = end

    return chunks
