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


def prompt_make_next_ai_message_with_documents(messages: List[Message], documents: List[PostProcessedDocument]) -> str:
    return f"""
Documents you may source information from if useful (use citations):
===================================
{format_documents(documents)}

Chat history:
===================================
{format_messages(messages)}

The next message in the conversion:
===================================
<{SYSTEM_NAME}>:
"""


def prompt_generate_question_from_chat_history(messages: List[Message]) -> str:
    if len(messages) == 1:
        return f"""
You are a completion generator. You should produce queries used to search in a search engine.
Produce a standalone question from the following message from a user. If the message isn't a question,
respond with the exact string "NO_QUESTION".

Message from user:
{messages[0].content}

Standalone question:
"""

    history = messages[:-1]
    last = messages[-1]
    return f"""
You are a completion generator. You should only produce queries used to search in a search engine.
Combine the chat history and follow up question into a standalone question. If the follow up question isn't a question,
respond with the exact string "NO_QUESTION".

Chat History:
{format_messages(history)}

Follow up question:
{last.content}

Standalone question:
"""


def prompt_post_process_doc_for_question(doc_text: str, question: str) -> str:
    return f'''
You will be provided with text delimited by triple quotes. If it the text contains information related to
the question "{question}", extract at most 3 quotes that are strictly related to answering the question
into a bulleted list like the following

- "a quote from the file..."
- "another quote from the file..."
...
- "the last quote from the file..."

If the text does not contain any related quotes,
then simply write \"No information in the document.\"

"""{doc_text}"""
'''
