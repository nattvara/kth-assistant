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

    params = Params(max_new_tokens=300)
    params.stop_strings = ['</quotes>']

    handle = LLMService.dispatch_prompt(prompt, chat.llm_model_name, params)
    await LLMService.wait_for_handle(handle)

    response = handle.response
    response = response.replace('</quotes>', '')
    response = response.replace('</quotes', '')

    return PostProcessedDocument(doc.name, doc.url, response)
