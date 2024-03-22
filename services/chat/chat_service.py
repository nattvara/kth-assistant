from db.models import Chat, Message, Session, Course
from services.chat.system import SYSTEM_PROMPT
from services.llm.llm import LLMService
import services.llm.prompts as prompts
from llms.config import Params
import db.actions.chat_config


class ChatServiceException(Exception):
    pass


class ChatService:

    @staticmethod
    def start_new_chat_for_session_and_course(session: Session, course: Course) -> Chat:
        config = db.actions.chat_config.get_random_chat_config()
        if config is None:
            raise ChatServiceException("no valid chat config.")

        params = Params()
        params.system_prompt = SYSTEM_PROMPT
        params.stop_strings = ['<student>', '<student', '<Student', '<Student>']
        chat = Chat(
            course=course,
            session=session,
            model_name=config.model_name,
            model_params=params,
            index_type=config.index_type
        )
        chat.save()
        return chat

    @staticmethod
    def request_next_message(chat: Chat) -> Message:
        messages = [message for message in chat.messages]
        prompt = prompts.prompt_make_next_ai_message(messages)

        handle = LLMService.dispatch_prompt(prompt, chat.model_name, chat.model_params)

        next_message = Message(chat=chat, content=None, sender=Message.Sender.ASSISTANT, prompt_handle=handle)
        next_message.save()

        return next_message
