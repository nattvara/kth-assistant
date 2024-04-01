from typing import List

from services.llm.llm import LLMService
from db.models import Message, Chat
from services.llm.prompts import (
    prompt_generate_question_from_chat_history,
    prompt_generate_keyword_query_from_chat_history
)
from llms.config import Params
from config.logger import log


async def generate_question_from_messages(messages: List[Message], chat: Chat) -> str:
    log().debug(f"generating questions for message in chat {chat.id}")

    params = Params(max_new_tokens=200)
    params.stop_strings = ['</question>']

    prompt = prompt_generate_question_from_chat_history(messages, chat.language)
    handle = LLMService.dispatch_prompt(prompt, chat.llm_model_name, params)
    await LLMService.wait_for_handle(handle)

    response = handle.response
    response = response.replace('</question>', '')
    response = response.replace('</question', '')
    response = response.strip()

    return response


async def generate_keyword_query_from_messages(messages: List[Message], chat: Chat) -> str:
    log().debug(f"generating keyword query for message in chat {chat.id}")

    params = Params(max_new_tokens=200)
    params.stop_strings = ['</query>']

    prompt = prompt_generate_keyword_query_from_chat_history(messages, chat.language, chat.course.description)
    handle = LLMService.dispatch_prompt(prompt, chat.llm_model_name, params)
    await LLMService.wait_for_handle(handle)

    response = handle.response
    response = response.replace('</query>', '')
    response = response.replace('</query', '')
    response = response.strip()

    return response
