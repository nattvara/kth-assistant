from typing import List

from services.llm.supported_models import LLMModel, EMBEDDING_MODELS, get_enum_from_enum_value
from services.llm.prompts import prompt_create_document_summary
from services.index.chunks import split_text_with_overlap
from llms.openai import truncate_text_to_token_limit
import services.index.opensearch as search
from db.models import Url, Snapshot
import config.settings as settings
from llms.config import Params
import services.llm.llm as llm
from config.logger import log


class IndexService:

    def __init__(self):
        self.client = search.get_client()

    async def index_url(self, url: Url):
        if not search.index_exists(self.client, url.snapshot.id):
            search.create_index(self.client, url.snapshot.id)

        summary = await self._create_document_summary(url.content.text)

        chunks = split_text_with_overlap(url.content.text)
        for idx, chunk in enumerate(chunks):
            document_text = self._create_document_text(idx, len(chunks), chunk, summary)
            sfr_embedding_mistral = await self._get_sfr_embedding_mistral_embeddings(document_text)
            text_embedding_3_large = await self._get_text_embedding_3_large_embeddings(document_text)

            search.index_document(self.client, url.snapshot, f"{url.id}-{idx}", {
                'name': url.content.name,
                'text': document_text,
                'text_raw': chunk,
                'url': url.href,
                'sfr_embedding_mistral': sfr_embedding_mistral,
                'text_embedding_3_large': text_embedding_3_large,
            })

        url.refresh()
        url.state = Url.States.INDEXED
        url.save()

    async def _create_document_summary(self, text: str) -> str:
        # using the openai tokeniser, which may not yield the same token count as
        # the model set in MODEL_USED_FOR_SUMMARIES. However, it's a decent estimate
        truncated_text = truncate_text_to_token_limit(text, 7500)

        if len(truncated_text) != len(text):
            log().info(f"text used for summary was truncated from {len(text)} to {len(truncated_text)}")

        log().info(f"creating summary for text: {truncated_text}")
        params = Params(max_new_tokens=100)
        params.stop_strings = ['</s>']

        model = get_enum_from_enum_value(settings.get_settings().MODEL_USED_FOR_SUMMARIES)

        prompt = prompt_create_document_summary(truncated_text)
        handle = llm.LLMService.dispatch_prompt(prompt, model, params)
        handle = await llm.LLMService.wait_for_handle(handle)

        summary = handle.response
        log().info(f"summary was: {summary}")
        return summary

    def _create_document_text(self, chunk_idx: int, chunk_count: int, text: str, summary: str) -> str:
        return f"""
Document chunk: {chunk_idx + 1}/{chunk_count}
Document summary: {summary}
Chunk content: {text}
        """.strip()

    async def _get_sfr_embedding_mistral_embeddings(self, text: str) -> List[float]:
        log().debug("requesting SALESFORCE_SFR_EMBEDDING_MISTRAL embedding...")
        handle = llm.LLMService.dispatch_prompt(text, LLMModel.SALESFORCE_SFR_EMBEDDING_MISTRAL)
        handle = await llm.LLMService.wait_for_handle(handle, timeout_seconds=20 * 60)
        return handle.embedding

    async def _get_text_embedding_3_large_embeddings(self, text: str) -> List[float]:
        log().debug("requesting OPENAI_TEXT_EMBEDDING_3_LARGE embedding...")
        handle = llm.LLMService.dispatch_prompt(text, LLMModel.OPENAI_TEXT_EMBEDDING_3_LARGE)
        handle = await llm.LLMService.wait_for_handle(handle)
        return handle.embedding

    def query_index(self, snapshot: Snapshot, query: str) -> List[search.Document]:
        return search.search_index(self.client, snapshot.id, query)

    async def query_index_with_vector(
        self,
        snapshot: Snapshot,
        question: str,
        embedding_model: LLMModel
    ) -> List[search.Document]:
        handle = llm.LLMService.dispatch_prompt(question, embedding_model)
        handle = await llm.LLMService.wait_for_handle(handle)

        return search.search_index_with_vector(
            self.client,
            snapshot.id,
            vector=handle.embedding,
            field_name=EMBEDDING_MODELS[embedding_model]
        )
