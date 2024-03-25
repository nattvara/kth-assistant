from typing import List

from services.llm.prompts import prompt_generate_question_from_chat_history
from services.llm.llm import LLMService
from db.models import Message, Chat
from llms.config import Params
from config.logger import log


async def generate_question_from_messages(messages: List[Message], chat: Chat) -> str:
    log().debug(f"generating questions for message in chat {chat.id}")

    prompt = prompt_generate_question_from_chat_history(messages)
    handle = LLMService.dispatch_prompt(prompt, chat.model_name, Params())
    await LLMService.wait_for_handle(handle)

    return handle.response
