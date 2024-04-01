from typing import List

from services.llm.prompts import prompt_generate_question_from_chat_history
from services.llm.llm import LLMService
from db.models import Message, Chat
from llms.config import Params
from config.logger import log


async def generate_question_from_messages(messages: List[Message], chat: Chat) -> str:
    log().debug(f"generating questions for message in chat {chat.id}")

    params = Params()
    params.stop_strings = ['</question>']

    prompt = prompt_generate_question_from_chat_history(messages, chat.language)
    handle = LLMService.dispatch_prompt(prompt, chat.llm_model_name, params)
    await LLMService.wait_for_handle(handle)

    response = handle.response
    response = response.replace('</question>', '')
    response = response.replace('</question', '')
    response = response.strip()

    return response
