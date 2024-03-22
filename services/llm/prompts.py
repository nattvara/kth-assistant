from typing import List

from services.llm.formatters import format_messages
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
<{SYSTEM_NAME}>:
"""
