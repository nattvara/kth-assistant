from typing import List

from services.llm.supported_models import LLMModel, EMBEDDING_MODELS
from services.index.chunks import split_text_with_overlap
import services.index.opensearch as search
from db.models import Url, Snapshot
import services.llm.llm as llm
from config.logger import log


class IndexService:

    def __init__(self):
        self.client = search.get_client()

    async def index_url(self, url: Url):
        if not search.index_exists(self.client, url.snapshot.id):
            search.create_index(self.client, url.snapshot.id)

        chunks = split_text_with_overlap(url.content.text)
        for idx, chunk in enumerate(chunks):
            sfr_embedding_mistral = await self._get_sfr_embedding_mistral_embeddings(chunk)
            text_embedding_3_large = await self._get_text_embedding_3_large_embeddings(chunk)

            search.index_document(self.client, url.snapshot, f"{url.id}-{idx}", {
                'name': url.content.name,
                'text': chunk,
                'url': url.href,
                'sfr_embedding_mistral': sfr_embedding_mistral,
                'text_embedding_3_large': text_embedding_3_large,
            })

        url.refresh()
        url.state = Url.States.INDEXED
        url.save()

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
