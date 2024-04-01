import asyncio

from services.chat.questions import generate_question_from_messages
from db.models import Chat, Message, Session, Course, Snapshot
from services.index.supported_indices import IndexType
from services.chat.docs import post_process_document
from services.crawler.crawler import CrawlerService
from services.chat.system import get_system_prompt
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
        params.system_prompt = get_system_prompt()
        params.stop_strings = ['<|user|>', '<|user', '<|assistant|>', '<|assistant']
        chat = Chat(
            course=course,
            session=session,
            llm_model_name=config.llm_model_name,
            llm_model_params=params,
            index_type=config.index_type
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

        if chat.index_type == IndexType.FULL_TEXT_SEARCH:
            return await ChatService.request_next_message_with_full_text_search_index(chat)

        raise UnsupportedIndexTypeException(f"cannot request new message for index type {chat.index_type} as"
                                            f"it is not supported")

    @staticmethod
    def request_next_message_without_index(chat: Chat) -> Message:
        messages = [message for message in chat.messages]
        prompt = prompts.prompt_make_next_ai_message(messages)

        handle = LLMService.dispatch_prompt(prompt, chat.llm_model_name, chat.llm_model_params)

        next_message = Message(chat=chat, content=None, sender=Message.Sender.ASSISTANT, prompt_handle=handle)
        next_message.save()

        return next_message

    @staticmethod
    async def request_next_message_with_full_text_search_index(chat: Chat) -> Message:
        messages = [message for message in chat.messages]

        question = await generate_question_from_messages(messages, chat)
        if 'NO_QUESTION' in question.strip().upper():
            return ChatService.request_next_message_without_index(chat)

        snapshot = ChatService.find_most_recent_snapshot_for_chat(chat)

        index = IndexService()
        docs = index.query_index(snapshot, query=question)

        post_processed_docs = list(await asyncio.gather(
            *[post_process_document(chat, doc, question) for doc in docs]
        ))

        prompt = prompts.prompt_make_next_ai_message_with_documents(messages, post_processed_docs)
        handle = LLMService.dispatch_prompt(prompt, chat.llm_model_name, chat.llm_model_params)

        next_message = Message(chat=chat, content=None, sender=Message.Sender.ASSISTANT, prompt_handle=handle)
        next_message.save()

        return next_message
