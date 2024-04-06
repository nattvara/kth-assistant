import pytest

from services.index.supported_indices import IndexType
from services.chat.chat_service import ChatService
from services.llm.supported_models import LLMModel
from db.models import Message, Course, ChatConfig


@pytest.mark.asyncio
async def test_chat_service_can_produce_message_for_chat_without_any_index(mocker, new_chat):
    mock_prompt = mocker.patch('services.llm.prompts.prompt_make_next_ai_message')
    new_chat.add_some_messages()
    messages = [message for message in new_chat.chat.messages]

    message = await ChatService.request_next_message(new_chat.chat)

    mock_prompt.assert_called_once()
    mock_prompt.assert_called_with(messages)
    assert len(new_chat.chat.messages) == len(messages) + 1
    assert message.sender == message.Sender.ASSISTANT


@pytest.mark.asyncio
async def test_chat_service_retrieve_list_of_chats_with_more_than_one_message(authenticated_session):
    config = ChatConfig(llm_model_name=LLMModel.MISTRAL_7B_INSTRUCT, index_type=IndexType.NO_INDEX)
    config.save()

    course1 = Course(canvas_id="41428", snapshot_lifetime_in_mins=60)
    course1.save()
    course2 = Course(canvas_id="41674", snapshot_lifetime_in_mins=60)
    course2.save()

    c1 = ChatService.start_new_chat_for_session_and_course(authenticated_session.session, course1)
    c2 = ChatService.start_new_chat_for_session_and_course(authenticated_session.session, course1)  # noqa
    c3 = ChatService.start_new_chat_for_session_and_course(authenticated_session.session, course2)

    Message(sender=Message.Sender.STUDENT, content=f'Hello!', chat=c1).save()
    Message(sender=Message.Sender.STUDENT, content=f'Hello!', chat=c3).save()

    chats = ChatService.find_chats_with_messages_in_course(course1)

    assert len(chats) == 1
    assert chats[0].id == c1.id
