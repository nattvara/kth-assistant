from typing import List
import asyncio

from db.actions.faq_snapshot import find_latest_faq_snapshot_for_course
from services.chat.questions import generate_question_from_messages, generate_keyword_query_from_messages
from services.index.supported_indices import IndexType, is_post_processing_index
from db.models import Chat, Message, Session, Course, Snapshot, FaqSnapshot
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
    def find_chats_with_messages_in_course(course: Course) -> List[Chat]:
        chats = course.chats
        out = []
        for chat in chats:
            if len(chat.messages) > 0:
                out.append(chat)
        return out

    @staticmethod
    def create_faq_snapshot(course: Course) -> FaqSnapshot:
        snapshot = FaqSnapshot(course=course)
        snapshot.save()
        return snapshot

    @staticmethod
    def get_most_recent_faq_snapshot(course: Course) -> FaqSnapshot:
        snapshot = find_latest_faq_snapshot_for_course(course)
        if snapshot is None:
            raise ChatServiceException(f"no faq snapshot found for course, {course.canvas_id}: {course.name}")
        return snapshot

    @staticmethod
    async def start_next_message(chat: Chat, next_message: Message) -> Message:
        if chat.index_type == IndexType.NO_INDEX:
            return ChatService._generate_next_message_without_index(chat, next_message)

        should_post_process = is_post_processing_index(chat.index_type)

        if chat.index_type in [IndexType.FULL_TEXT_SEARCH, IndexType.FULL_TEXT_SEARCH_WITH_POST_PROCESSING]:
            return await ChatService._generate_next_message_with_full_text_search_index(chat, next_message, should_post_process)

        if chat.index_type in [
            IndexType.VECTOR_SEARCH_SALESFORCE_SFR_EMBEDDING_MISTRAL,
            IndexType.VECTOR_SEARCH_SALESFORCE_SFR_EMBEDDING_MISTRAL_WITH_POST_PROCESSING,
        ]:
            return await ChatService._generate_next_message_with_vector_search(
                chat,
                next_message,
                LLMModel.SALESFORCE_SFR_EMBEDDING_MISTRAL,
                should_post_process
            )

        if chat.index_type in [
            IndexType.VECTOR_SEARCH_OPENAI_TEXT_EMBEDDING_3_LARGE,
            IndexType.VECTOR_SEARCH_OPENAI_TEXT_EMBEDDING_3_LARGE_WITH_POST_PROCESSING,
        ]:
            return await ChatService._generate_next_message_with_vector_search(
                chat,
                next_message,
                LLMModel.OPENAI_TEXT_EMBEDDING_3_LARGE,
                should_post_process
            )

        raise UnsupportedIndexTypeException(f"cannot request new message for index type {chat.index_type} as"
                                            f" it is not supported")

    @staticmethod
    def _generate_next_message_without_index(chat: Chat, next_message: Message) -> Message:
        messages = [message for message in chat.messages[:-1]]
        prompt = prompts.prompt_make_next_ai_message(messages)

        handle = LLMService.dispatch_prompt(prompt, chat.llm_model_name, chat.llm_model_params)

        next_message.refresh()
        next_message.prompt_handle = handle
        next_message.save()

        return next_message

    @staticmethod
    async def _generate_next_message_with_full_text_search_index(chat: Chat, next_message: Message, should_post_process_docs: bool) -> Message:
        messages = [message for message in chat.messages[:-1]]

        question = await generate_question_from_messages(messages, chat)
        if 'NO_QUESTION' in question.strip().upper():
            return ChatService._generate_next_message_without_index(chat, next_message)

        keyword_query = await generate_keyword_query_from_messages(messages, chat)

        snapshot = ChatService.find_most_recent_snapshot_for_chat(chat)

        index = IndexService()
        docs = index.query_index(snapshot, query=keyword_query)

        if should_post_process_docs:
            return await ChatService._generate_next_message_with_post_processed_docs(messages, chat, next_message, docs, question)

        return await ChatService._generate_next_message_with_docs(messages, chat, next_message, docs)

    @staticmethod
    async def _generate_next_message_with_vector_search(
        chat: Chat,
        next_message: Message,
        embedding_model: LLMModel,
        should_post_process_docs: bool
    ) -> Message:
        messages = [message for message in chat.messages[:-1]]

        question = await generate_question_from_messages(messages, chat)
        if 'NO_QUESTION' in question.strip().upper():
            return ChatService._generate_next_message_without_index(chat, next_message)

        snapshot = ChatService.find_most_recent_snapshot_for_chat(chat)

        index = IndexService()
        docs = await index.query_index_with_vector(
            snapshot,
            question=question,
            embedding_model=embedding_model
        )

        if should_post_process_docs:
            return await ChatService._generate_next_message_with_post_processed_docs(messages, chat, next_message, docs, question)

        return await ChatService._generate_next_message_with_docs(messages, chat, next_message, docs)

    @staticmethod
    async def _generate_next_message_with_docs(
        messages: List[Message],
        chat: Chat,
        next_message: Message,
        docs: List[Document],
    ) -> Message:
        prompt = prompts.prompt_make_next_ai_message_with_documents(messages, docs)
        handle = LLMService.dispatch_prompt(prompt, chat.llm_model_name, chat.llm_model_params)

        next_message.refresh()
        next_message.prompt_handle = handle
        next_message.save()

        return next_message

    @staticmethod
    async def _generate_next_message_with_post_processed_docs(
        messages: List[Message],
        chat: Chat,
        next_message: Message,
        docs: List[Document],
        question: str
    ) -> Message:
        post_processed_docs = list(await asyncio.gather(
            *[post_process_document(chat, doc, question) for doc in docs]
        ))

        prompt = prompts.prompt_make_next_ai_message_with_post_processed_documents(messages, post_processed_docs)
        handle = LLMService.dispatch_prompt(prompt, chat.llm_model_name, chat.llm_model_params)

        next_message.refresh()
        next_message.prompt_handle = handle
        next_message.save()

        return next_message
