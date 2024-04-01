from typing import List

from services.chat.docs import PostProcessedDocument
from db.models import Message


def format_messages(messages: List[Message]) -> str:
    out = ""
    for message in messages:
        out += format_message(message) + "\n"
    return out


def format_message(message: Message) -> str:
    if message.sender == Message.Sender.STUDENT:
        sender = 'user'
        content = message.content
    else:
        sender = 'assistant'
        content = message.prompt_handle.response
    return f"<|{sender}|> {content}"


def format_documents(docs: List[PostProcessedDocument]) -> str:
    out = ""
    for doc in docs:
        out += format_document(doc) + "\n"
    return out


def format_document(doc: PostProcessedDocument) -> str:
    return f"""
name: {doc.name}
url: {doc.url}
```
{doc.text}
```
"""
