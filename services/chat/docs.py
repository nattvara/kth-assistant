from services.index.opensearch import Document
from services.llm.llm import LLMService
import services.llm.prompts as prompts
from llms.config import Params
from config.logger import log
from db.models import Chat


class PostProcessedDocument:

    def __init__(self, name: str, url: str, text: str):
        self.name = name
        self.url = url
        self.text = text


async def post_process_document(chat: Chat, doc: Document, question: str) -> PostProcessedDocument:
    log().debug(f"post processing doc {doc.name}")

    prompt = prompts.prompt_post_process_doc_for_question(doc.text, question)

    handle = LLMService.dispatch_prompt(prompt, chat.model_name, Params(max_new_tokens=400))
    await LLMService.wait_for_handle(handle)

    return PostProcessedDocument(doc.name, doc.url, handle.response)
