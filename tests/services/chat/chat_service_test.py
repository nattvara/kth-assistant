import pytest

from db.models import Message, Course, ChatConfig, Chat, FeedbackQuestion, Feedback, PromptHandle, FaqSnapshot, Faq
from services.index.supported_indices import IndexType
from db.models.feedback_question import FAQ_TRIGGER
from db.models.feedback import QUESTION_UNANSWERED
from services.chat.chat_service import ChatService
from services.llm.supported_models import LLMModel


@pytest.fixture
def create_chat_simulation(valid_course, authenticated_session):
    def func():
        class ChatSimulation:
            def __init__(self, chat: Chat, course: Course):
                self.course = course
                self.chat = chat

            def add_messages(self, number_of_messages: int):
                for _ in range(number_of_messages):
                    msg_student = Message(sender=Message.Sender.STUDENT, content='Hello from student!', chat=self.chat)
                    msg_student.save()
                    handle = PromptHandle(prompt="hi", llm_model_name=self.chat.llm_model_name, response="hello")
                    handle.save()
                    msg_assistant = Message(sender=Message.Sender.ASSISTANT, content='Hello student!', chat=self.chat)
                    msg_assistant.prompt_handle = handle
                    msg_assistant.save()

        c = Chat(
            course=valid_course,
            session=authenticated_session.session,
            llm_model_name=authenticated_session.session.default_llm_model_name,
            index_type=authenticated_session.session.default_index_type
        )
        c.save()

        return ChatSimulation(c, valid_course)
    return func


@pytest.mark.asyncio
async def test_chat_service_can_produce_message_for_chat_without_any_index(mocker, new_chat):
    mock_prompt = mocker.patch('services.llm.prompts.prompt_make_next_ai_message')
    new_chat.add_some_messages()
    messages = [message for message in new_chat.chat.messages]

    next_message = Message(chat=new_chat.chat, content=None, sender=Message.Sender.ASSISTANT)
    next_message.save()

    message = await ChatService.start_next_message(new_chat.chat, next_message)

    mock_prompt.assert_called_once()
    mock_prompt.assert_called_with(messages)
    assert len(new_chat.chat.messages) == len(messages) + 1
    assert message.sender == message.Sender.ASSISTANT


@pytest.mark.asyncio
async def test_message_state_is_set_to_ready_after_message_has_been_started(new_chat):
    next_message = Message(
        chat=new_chat.chat,
        content=None,
        sender=Message.Sender.ASSISTANT,
        state=Message.States.PENDING
    )
    next_message.save()

    assert next_message.state == Message.States.PENDING
    await ChatService.start_next_message(new_chat.chat, next_message)
    assert next_message.state == Message.States.READY


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

    Message(sender=Message.Sender.STUDENT, content="Hello!", chat=c1).save()
    Message(sender=Message.Sender.STUDENT, content="Hello!", chat=c3).save()

    chats = ChatService.find_chats_with_messages_in_course(course1)

    assert len(chats) == 1
    assert chats[0].id == c1.id


@pytest.mark.asyncio
async def test_chat_service_can_retrieve_the_most_recent_faq_snapshot(valid_course):
    snapshot1 = ChatService.create_faq_snapshot(valid_course)  # noqa
    snapshot2 = ChatService.create_faq_snapshot(valid_course)  # noqa
    snapshot3 = ChatService.create_faq_snapshot(valid_course)  # noqa

    snapshot = ChatService.get_most_recent_faq_snapshot(valid_course)

    assert snapshot.id == snapshot3.id


@pytest.mark.asyncio
async def test_chat_service_can_trigger_feedback_message_on_message_number_in_chat_number(create_chat_simulation):
    question_1 = FeedbackQuestion(
        trigger="chat:2:message:4",
        question_en="Good?",
        question_sv="Bra?",
        extra_data_en={'choices': ['yes', 'no']},
        extra_data_sv={'choices': ['ja', 'nej']},
    )
    question_1.save()

    chat_1 = create_chat_simulation()
    chat_1.add_messages(13)
    chat_2 = create_chat_simulation()
    chat_2.add_messages(3)

    # At this point no feedback should have been triggered
    assert len(chat_2.chat.messages) == 6

    msg = Message(chat=chat_2.chat, content='some question', sender=Message.Sender.STUDENT)
    msg.save()
    next_message = Message(
        chat=chat_2.chat,
        content=None,
        sender=Message.Sender.ASSISTANT,
        state=Message.States.PENDING
    )
    next_message.save()

    await ChatService.start_next_message(chat_2.chat, next_message)

    # should be 3 new messages added
    assert len(chat_2.chat.messages) == 9
    assert chat_2.chat.messages[-1].sender == Message.Sender.FEEDBACK

    # Empty feedback should have been recorded
    feedback = Feedback.select().filter(
        Feedback.feedback_question == question_1
    ).filter(
        Feedback.message == chat_2.chat.messages[-1]
    )
    assert feedback.exists()
    assert feedback.first().answer == QUESTION_UNANSWERED


@pytest.mark.asyncio
async def test_chat_service_can_trigger_feedback_message_on_faq_messages(create_chat_simulation):
    question_1 = FeedbackQuestion(
        trigger=FAQ_TRIGGER,
        question_en="Good?",
        question_sv="Bra?",
        extra_data_en={'type': 'thumbs', 'choices': ['thumbs_up', 'thumbs_down']},
        extra_data_sv={'type': 'thumbs', 'choices': ['thumbs_up', 'thumbs_down']},
    )
    question_1.save()

    chat_1 = create_chat_simulation()
    faq_snapshot = FaqSnapshot(course=chat_1.course)
    faq_snapshot.save()
    faq = Faq(question="some question", snapshot=faq_snapshot)
    faq.save()

    msg = Message(chat=chat_1.chat, content="some question", sender=Message.Sender.STUDENT, faq=faq)
    msg.save()
    next_message = Message(
        chat=chat_1.chat,
        content=None,
        sender=Message.Sender.ASSISTANT,
        state=Message.States.PENDING
    )
    next_message.save()

    await ChatService.start_next_message(chat_1.chat, next_message)

    # an extra message should've been added
    assert len(chat_1.chat.messages) == 3
    assert chat_1.chat.messages[-1].sender == Message.Sender.FEEDBACK

    # Empty feedback should have been recorded
    feedback = Feedback.select().filter(
        Feedback.feedback_question == question_1
    ).filter(
        Feedback.message == chat_1.chat.messages[-1]
    )
    assert feedback.exists()
    assert feedback.first().answer == QUESTION_UNANSWERED
