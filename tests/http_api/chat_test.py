from db.models import Chat, Message, PromptHandle, ChatConfig, Faq, Session
from services.index.supported_indices import IndexType
from services.llm.supported_models import LLMModel
from services.chat.chat_service import ChatService


def test_chats_are_tied_to_course_room(api_client, authenticated_session, valid_course):
    response = api_client.post(f'/course/{valid_course.canvas_id}/chat', headers=authenticated_session.headers)
    chat = Chat.filter(Chat.public_id == response.json()['public_id']).first()

    assert response.status_code == 200
    assert chat.course.canvas_id == valid_course.canvas_id


def test_chats_are_tied_to_session(api_client, authenticated_session, valid_course):
    response = api_client.post(f'/course/{valid_course.canvas_id}/chat', headers=authenticated_session.headers)
    chat = Chat.filter(Chat.public_id == response.json()['public_id']).first()

    assert response.status_code == 200
    assert chat.session.public_id == authenticated_session.session.public_id


def test_start_chat_fails_with_invalid_course_id(api_client, authenticated_session):
    invalid_course = 'something_bogus'

    response = api_client.post(f'/course/{invalid_course}/chat', headers=authenticated_session.headers)

    assert response.status_code == 404


def test_start_chat_fails_with_invalid_session(api_client, authenticated_session, valid_course):
    authenticated_session.session.is_valid = False
    authenticated_session.session.save()

    response = api_client.post(f'/course/{valid_course.canvas_id}/chat', headers=authenticated_session.headers)

    assert response.status_code == 401


def test_user_can_send_message_to_chat(api_client, authenticated_session, new_chat):
    url = f'/course/{new_chat.course.canvas_id}/chat/{new_chat.chat.public_id}/messages'
    response = api_client.post(url, json={'content': 'foo'}, headers=authenticated_session.headers)

    new_chat.chat.refresh()
    assert response.status_code == 201
    assert new_chat.chat.messages[0].content == 'foo'
    assert new_chat.chat.messages[0].sender == Message.Sender.STUDENT


def test_user_can_get_messages_in_chat(api_client, authenticated_session, new_chat):
    new_chat.add_some_messages()

    url = f'/course/{new_chat.course.canvas_id}/chat/{new_chat.chat.public_id}/messages'
    response = api_client.get(url, headers=authenticated_session.headers)

    messages = response.json()['messages']

    assert response.status_code == 200
    assert len(messages) == len(new_chat.chat.messages)
    for idx, message in enumerate(messages):
        assert new_chat.chat.messages[idx].content == message['content']
        assert new_chat.chat.messages[idx].sender == message['sender']


def test_user_get_single_message_in_chat(api_client, authenticated_session, new_chat):
    new_chat.add_some_messages()
    message = new_chat.chat.messages[0]

    url = f'/course/{new_chat.course.canvas_id}/chat/{new_chat.chat.public_id}/messages/{message.message_id}'
    response = api_client.get(url, headers=authenticated_session.headers)

    assert response.status_code == 200
    assert response.json()['message_id'] == message.message_id
    assert response.json()['content'] == message.content


def test_new_student_message_creates_streaming_assistant_message(
    api_client,
    authenticated_session,
    new_chat,
    llm_prompt
):
    url = f'/course/{new_chat.course.canvas_id}/chat/{new_chat.chat.public_id}/messages'
    api_client.post(url, json={'content': llm_prompt}, headers=authenticated_session.headers)
    response = api_client.get(url, headers=authenticated_session.headers).json()

    assistant_msg = new_chat.chat.messages[1]
    new_chat.chat.refresh()

    assert len(new_chat.chat.messages) == 2
    assert assistant_msg.sender == Message.Sender.ASSISTANT
    assert response['messages'][1]['streaming']


def test_new_student_messages_creates_prompt_handle(api_client, authenticated_session, new_chat, llm_prompt):
    url = f'/course/{new_chat.course.canvas_id}/chat/{new_chat.chat.public_id}/messages'
    api_client.post(url, json={'content': llm_prompt}, headers=authenticated_session.headers)

    assistant_msg = new_chat.chat.messages[1]
    new_chat.chat.refresh()

    assert PromptHandle.select().filter(PromptHandle.id == assistant_msg.prompt_handle).exists()


def test_assistant_messages_returns_prompt_handle_response_if_done_streaming(
    api_client,
    authenticated_session,
    new_chat,
    llm_prompt
):
    url = f'/course/{new_chat.course.canvas_id}/chat/{new_chat.chat.public_id}/messages'
    api_client.post(url, json={'content': llm_prompt}, headers=authenticated_session.headers)

    assistant_msg = new_chat.chat.messages[1]
    handle = assistant_msg.prompt_handle
    handle.state = PromptHandle.States.FINISHED
    handle.response = "foo"
    handle.save()

    url = f'/course/{new_chat.course.canvas_id}/chat/{new_chat.chat.public_id}/messages'
    response = api_client.get(url, headers=authenticated_session.headers).json()

    assert response['messages'][1]['content'] == 'foo'


def test_chat_config_is_selected_randomly_from_chat_configs(
    mocker,
    api_client,
    authenticated_session,
    valid_course,
):
    config_1 = ChatConfig(llm_model_name=LLMModel.MISTRAL_7B_INSTRUCT, index_type=IndexType.NO_INDEX)
    config_2 = ChatConfig(llm_model_name=LLMModel.OPENAI_GPT4, index_type=IndexType.NO_INDEX)
    config_1.save()
    config_2.save()
    mocker.patch(
        'db.actions.chat_config.get_random_chat_config',
        side_effect=[config_1, config_2]
    )

    url = f'/course/{valid_course.canvas_id}/chat'

    response = api_client.post(url, headers=authenticated_session.headers)
    chat = Chat.filter(Chat.public_id == response.json()['public_id']).first()

    assert chat.llm_model_name == config_1.llm_model_name

    response = api_client.post(url, headers=authenticated_session.headers)
    chat = Chat.filter(Chat.public_id == response.json()['public_id']).first()
    assert chat.llm_model_name == config_2.llm_model_name


def test_chats_inherit_the_language_of_the_course_they_belong_to(api_client, authenticated_session, valid_course):
    valid_course.language = valid_course.Language.SWEDISH
    valid_course.save()

    response = api_client.post(f'/course/{valid_course.canvas_id}/chat', headers=authenticated_session.headers)
    chat = Chat.filter(Chat.public_id == response.json()['public_id']).first()

    assert response.status_code == 200
    assert chat.language == valid_course.Language.SWEDISH


def test_most_recent_faqs_can_be_retrieved(api_client, authenticated_session, valid_course):
    snapshot = ChatService.create_faq_snapshot(valid_course)
    faq_1 = Faq(question="And Why Do We Fall, Bruce?", snapshot=snapshot)
    faq_1.save()
    faq_2 = Faq(question="Why So Serious?", snapshot=snapshot)
    faq_2.save()

    response = api_client.post(f'/course/{valid_course.canvas_id}/chat', headers=authenticated_session.headers)

    assert response.status_code == 200
    assert response.json()['faqs'][0]['faq_id'] == faq_1.faq_id
    assert response.json()['faqs'][0]['question'] == faq_1.question
    assert response.json()['faqs'][1]['faq_id'] == faq_2.faq_id
    assert response.json()['faqs'][1]['question'] == faq_2.question


def test_first_message_in_chat_can_be_created_from_faq(api_client, authenticated_session, new_chat):
    snapshot = ChatService.create_faq_snapshot(new_chat.course)
    faq_1 = Faq(question="And Why Do We Fall, Bruce?", snapshot=snapshot)
    faq_1.save()

    url = f'/course/{new_chat.course.canvas_id}/chat/{new_chat.chat.public_id}/messages'
    response = api_client.post(url, json={'faq_id': faq_1.faq_id}, headers=authenticated_session.headers)

    new_chat.chat.refresh()
    assert response.status_code == 201
    assert new_chat.chat.messages[0].content == "And Why Do We Fall, Bruce?"
    assert new_chat.chat.messages[0].sender == Message.Sender.STUDENT

    # both messages should reference the faq
    assert new_chat.chat.messages[0].faq.id == faq_1.id
    assert new_chat.chat.messages[1].faq.id == faq_1.id


def test_chat_cannot_be_started_unless_consent_is_granted(api_client, valid_course):
    session = Session(default_llm_model_name=LLMModel.MISTRAL_7B_INSTRUCT, default_index_type=IndexType.NO_INDEX)
    session.save()
    headers = {'X-Session-ID': session.public_id}

    response = api_client.post(f'/course/{valid_course.canvas_id}/chat', headers=headers)
    assert response.status_code == 400

    session.consent = True
    session.save()

    response = api_client.post(f'/course/{valid_course.canvas_id}/chat', headers=headers)
    assert response.status_code == 200
