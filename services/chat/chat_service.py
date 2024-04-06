from typing import List
import asyncio

from services.chat.questions import generate_question_from_messages, generate_keyword_query_from_messages
from services.index.supported_indices import IndexType, is_post_processing_index
from db.models import Chat, Message, Session, Course, Snapshot
from services.chat.docs import post_process_document
from services.crawler.crawler import CrawlerService
from services.llm.supported_models import LLMModel
from services.chat.system import get_system_prompt
from services.index.opensearch import Document
from services.index.index import IndexService
from services.llm.llm import LLMService
import services.llm.prompts as prompts
from llms.config import Params
import db.actions.chat_config


class ChatServiceException(Exception):
    pass


class UnsupportedIndexTypeException(Exception):
    pass


class ChatService:

    @staticmethod
    def start_new_chat_for_session_and_course(session: Session, course: Course) -> Chat:
        config = db.actions.chat_config.get_random_chat_config()
        if config is None:
            raise ChatServiceException("no valid chat config.")

        params = Params()
        params.system_prompt = get_system_prompt(course.language, course.name, course.description)
        params.stop_strings = ['<|user|>', '<|user', '<|assistant|>', '<|assistant']
        chat = Chat(
            course=course,
            session=session,
            llm_model_name=config.llm_model_name,
            llm_model_params=params,
            index_type=config.index_type,
            language=course.language,
        )
        chat.save()
        return chat

    @staticmethod
    def find_most_recent_snapshot_for_chat(chat: Chat) -> Snapshot:
        return CrawlerService.current_snapshot(chat.course)

    @staticmethod
    async def request_next_message(chat: Chat) -> Message:
        if chat.index_type == IndexType.NO_INDEX:
            return ChatService.request_next_message_without_index(chat)

        should_post_process = is_post_processing_index(chat.index_type)

        if chat.index_type in [IndexType.FULL_TEXT_SEARCH, IndexType.FULL_TEXT_SEARCH_WITH_POST_PROCESSING]:
            return await ChatService.request_next_message_with_full_text_search_index(chat, should_post_process)

        if chat.index_type in [
            IndexType.VECTOR_SEARCH_SALESFORCE_SFR_EMBEDDING_MISTRAL,
            IndexType.VECTOR_SEARCH_SALESFORCE_SFR_EMBEDDING_MISTRAL_WITH_POST_PROCESSING,
        ]:
            return await ChatService.request_next_message_with_vector_search(
                chat,
                LLMModel.SALESFORCE_SFR_EMBEDDING_MISTRAL,
                should_post_process
            )

        if chat.index_type in [
            IndexType.VECTOR_SEARCH_OPENAI_TEXT_EMBEDDING_3_LARGE,
            IndexType.VECTOR_SEARCH_OPENAI_TEXT_EMBEDDING_3_LARGE_WITH_POST_PROCESSING,
        ]:
            return await ChatService.request_next_message_with_vector_search(
                chat,
                LLMModel.OPENAI_TEXT_EMBEDDING_3_LARGE,
                should_post_process
            )

        raise UnsupportedIndexTypeException(f"cannot request new message for index type {chat.index_type} as"
                                            f" it is not supported")

    @staticmethod
    def request_next_message_without_index(chat: Chat) -> Message:
        messages = [message for message in chat.messages]
        prompt = prompts.prompt_make_next_ai_message(messages)

        handle = LLMService.dispatch_prompt(prompt, chat.llm_model_name, chat.llm_model_params)

        next_message = Message(chat=chat, content=None, sender=Message.Sender.ASSISTANT, prompt_handle=handle)
        next_message.save()

        return next_message

    @staticmethod
    async def request_next_message_with_full_text_search_index(chat: Chat, should_post_process_docs: bool) -> Message:
        messages = [message for message in chat.messages]

        question = await generate_question_from_messages(messages, chat)
        if 'NO_QUESTION' in question.strip().upper():
            return ChatService.request_next_message_without_index(chat)

        keyword_query = await generate_keyword_query_from_messages(messages, chat)

        snapshot = ChatService.find_most_recent_snapshot_for_chat(chat)

        index = IndexService()
        docs = index.query_index(snapshot, query=keyword_query)

        if should_post_process_docs:
            return await ChatService.request_next_message_with_post_processed_docs(messages, chat, docs, question)

        return await ChatService.request_next_message_with_docs(messages, chat, docs)

    @staticmethod
    async def request_next_message_with_vector_search(
        chat: Chat,
        embedding_model: LLMModel,
        should_post_process_docs: bool
    ) -> Message:
        messages = [message for message in chat.messages]

        question = await generate_question_from_messages(messages, chat)
        if 'NO_QUESTION' in question.strip().upper():
            return ChatService.request_next_message_without_index(chat)

        snapshot = ChatService.find_most_recent_snapshot_for_chat(chat)

        index = IndexService()
        docs = await index.query_index_with_vector(
            snapshot,
            question=question,
            embedding_model=embedding_model
        )

        if should_post_process_docs:
            return await ChatService.request_next_message_with_post_processed_docs(messages, chat, docs, question)

        return await ChatService.request_next_message_with_docs(messages, chat, docs)

    @staticmethod
    async def request_next_message_with_docs(
        messages: List[Message],
        chat: Chat,
        docs: List[Document],
    ) -> Message:
        prompt = prompts.prompt_make_next_ai_message_with_documents(messages, docs)
        handle = LLMService.dispatch_prompt(prompt, chat.llm_model_name, chat.llm_model_params)

        next_message = Message(chat=chat, content=None, sender=Message.Sender.ASSISTANT, prompt_handle=handle)
        next_message.save()

        return next_message

    @staticmethod
    async def request_next_message_with_post_processed_docs(
        messages: List[Message],
        chat: Chat,
        docs: List[Document],
        question: str
    ) -> Message:
        post_processed_docs = list(await asyncio.gather(
            *[post_process_document(chat, doc, question) for doc in docs]
        ))

        prompt = prompts.prompt_make_next_ai_message_with_post_processed_documents(messages, post_processed_docs)
        handle = LLMService.dispatch_prompt(prompt, chat.llm_model_name, chat.llm_model_params)

        next_message = Message(chat=chat, content=None, sender=Message.Sender.ASSISTANT, prompt_handle=handle)
        next_message.save()

        return next_message
