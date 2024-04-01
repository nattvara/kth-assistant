from typing import List

from services.llm.formatters import format_messages, format_documents
from services.chat.docs import PostProcessedDocument
from db.models import Message


def prepend_system_prompt(system_prompt: str, prompt: str) -> str:
    return f"""
Chat rules:
===================================

{system_prompt}

{prompt}
""".strip()


def prompt_make_next_ai_message(messages: List[Message]) -> str:
    return f"""
Chat history:
===================================
{format_messages(messages)}
<|assistant|>
""".strip()


def prompt_make_next_ai_message_with_documents(messages: List[Message], documents: List[PostProcessedDocument]) -> str:
    return f"""
Documents you may source information from if useful (use citations):
===================================
{format_documents(documents)}

Chat history:
===================================
{format_messages(messages)}
<|assistant|>
""".strip()


def prompt_generate_question_from_chat_history(messages: List[Message], language: str) -> str:
    if language == 'en':
        language = 'English'
        standalone_question_example = "standalone question here..."
    elif language == 'sv':
        language = 'Swedish'
        standalone_question_example = "självständig fråga här..."
    else:
        raise ValueError(f"Unsupported language: {language}")

    if len(messages) == 1:
        return f"""
You are a completion generator. You should produce queries used to search in a search engine. Produce a standalone
question in {language} from a message from a user. You should use the following format:

<question lang="{language}">
{standalone_question_example}
</question>

If the message isn't a question, respond with the string NO_QUESTION, like this:
<question>
NO_QUESTION
</question>

The users' question: {messages[0].content}

<question lang="{language}">
""".strip()

    history = messages[:-1]
    last = messages[-1]
    return f"""
You are a completion generator. You should only produce queries used to search in a search engine.
Combine the chat history and follow up question into a standalone question in {language}.

<question lang="{language}">
{standalone_question_example}
</question>

If the message isn't a question, respond with the exact string "NO_QUESTION", like this:
<question>
NO_QUESTION
</question>

Chat History:
{format_messages(history)}

Follow up question from user:
{last.content}

<question lang="{language}">
""".strip()


def prompt_generate_keyword_query_from_chat_history(
    messages: List[Message],
    language: str,
    course_description: str
) -> str:
    if language == 'en':
        language = 'English'
        query_example = "search query for search engine with lots of keywords..."
    elif language == 'sv':
        language = 'Swedish'
        query_example = "sök fråga för sökmotor med massor av nyckelord..."
    else:
        raise ValueError(f"Unsupported language: {language}")

    if len(messages) == 1:
        return f"""
You are a query generator. You will produce queries used to search for documents in a search engine. Create a search
query based on the following question from the user. Make sure to include many keywords in the query. The query should
be on the following format

<query lang="{language}">
{query_example}
</query>

The documents belong to a course with the following description:
{course_description}

The users' question:
{messages[0].content}

<query lang="{language}">
""".strip()

    history = messages[:-1]
    last = messages[-1]
    return f"""
You are a query generator. You will produce queries used to search for documents in a search engine. Create a search
query based on the chat history and follow up question. Make sure to include many keywords in the query. The query
should be on the following format

<query lang="{language}">
{query_example}
</query>

The documents belong to a course with the following description:
{course_description}

Chat History:
{format_messages(history)}

Follow up question from user:
{last.content}

<query lang="{language}">
""".strip()


def prompt_post_process_doc_for_question(doc_text: str, question: str) -> str:
    return f'''You are an information extractor. You will be provided with one TEXT delimited by triple quotes. If the
text contains information related to a given QUESTION then extract at most 3 RELEVANT QUOTES that are strictly related
to answering the question. Do not provide a direct answer to the question. The quotes should be extracted into the
following format:

<quotes>
- "a quote from the file..."
- "another quote from the file..."
- "the last quote from the file..."
</quotes>

If the text does not contain any quotes that are relevant for the question, reply with the following

<quotes>
"No information in the document."
</quotes>

QUESTION:
"{question}"

TEXT:
"""{doc_text}"""

<quotes>
'''
