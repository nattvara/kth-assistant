from typing import List

from services.index.opensearch import Document
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

Generate the next assistant message within <s> </s> tags:

<s><|assistant|>
""".strip()


def prompt_make_next_ai_message_with_documents(
    messages: List[Message],
    documents: List[Document]
) -> str:
    return f"""
Documents you may source information from if useful (use citations):
===================================
{format_documents(documents)}

Chat history:
===================================
{format_messages(messages)}

Generate the next assistant message within <s> </s> tags:

<s><|assistant|>
""".strip()


def prompt_make_next_ai_message_with_post_processed_documents(
    messages: List[Message],
    documents: List[PostProcessedDocument]
) -> str:
    return f"""
Documents you may source information from if useful (use citations):
===================================
{format_documents(documents)}

Chat history:
===================================
{format_messages(messages)}

Generate the next assistant message within <s> </s> tags:

<s><|assistant|>
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


def prompt_common_questions(aggregated_chats: str, language: str, course_title: str) -> str:
    if language == 'en':
        language = 'English'
    elif language == 'sv':
        language = 'Swedish'
    else:
        raise ValueError(f"Unsupported language: {language}")

    return f"""
Consider these chat logs between an assistant and a set of users. Extract the most common questions the user asks the
assistant into a list of questions that start with <question> and end with </question> like this. Make sure the
questions are in the language: {language}. Make sure the questions are standalone, so if the question is a
followup question, make sure to include enough context so that question could be standalone, however, don't mention
{course_title} inside <question>.

<question>
user question here...
</question>
<question>
another question here
</question>

here are all the chat logs:
{aggregated_chats}
"""


def prompt_deduplicate_questions(questions: List[str]) -> str:
    questions_wrapped_in_tags = ''
    for question in questions:
        questions_wrapped_in_tags += f"<question>{question}</question>\n"

    return f"""
Consider this list of questions. De-duplicate the list and extract a list of unique questions. Make sure that you wrap
the questions in <question> tags like the following. Also reduce the number of questions by half, merge common
questions.

<question>
user question here...
</question>
<question>
another question here
</question>

Now, Here are all the questions
{questions_wrapped_in_tags}
"""


def prompt_extract_kattis_instruction_from_html(kattis_html: str) -> str:
    return f"""
You are a content extractor. Consider this html content that describes a kattis assignment (a code platform),
extract the assignment title, description, in and out data, and any other information into a structured text format

Ensure to extract all info. The input data is data that will be sent to the stdin of the program and the output data is
data that should be printed to stdout.

Make sure to extract the exact text and example as it is written. Recite it as it is. Do not translate it if it is
written in a language other than english. You should just reformat it so that it's easier to read.

Here is the HTML, extract the content in the same language as it is written:
{kattis_html}
"""


def prompt_create_document_summary(document: str, language: str) -> str:
    if language == 'en':
        language = 'English'
    elif language == 'sv':
        language = 'Swedish'
    else:
        raise ValueError(f"Unsupported language: {language}")

    return f'''
<s>
You are a commentator. Your task is to explain a document given in triple quotes.

Document:
"""{document}"""

[INST]
The document has been presented triple quotes. In clear and concise language, explain what can be found in the
document, in once sentence. The explanation must be in {language}.
[/INST]
'''.strip()
