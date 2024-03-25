from typing import List

from services.llm.formatters import format_messages, format_documents
from services.chat.docs import PostProcessedDocument
from services.chat.system import SYSTEM_NAME
from db.models import Message


def prepend_system_prompt(system_prompt: str, prompt: str) -> str:
    return f"""
Chat rules:
===================================

{system_prompt}

{prompt}
"""


def prompt_make_next_ai_message(messages: List[Message]) -> str:
    return f"""
Chat history:
===================================
{format_messages(messages)}

The next message in the conversion:
===================================
<{SYSTEM_NAME}>:
"""


def prompt_generate_question_from_chat_history(messages: List[Message]) -> str:
    history = messages[:-1]
    last = messages[-1]
    return f"""
You are a completion generator. You should only produce questions used to search in a vector database.
Combine the chat history and follow up question into a standalone question. If the follow up question isn't a question,
respond with the exact string "NO_QUESTION".

Chat History:
{format_messages(history)}

Follow up question:
{last.content}

Standalone question:
"""
