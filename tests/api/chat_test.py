from db.models import Course, Chat, Message


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


def test_user_get_messages_in_chat(api_client, authenticated_session, new_chat):
    new_chat.add_some_messages()

    url = f'/course/{new_chat.course.canvas_id}/chat/{new_chat.chat.public_id}/messages'
    response = api_client.get(url, headers=authenticated_session.headers)

    messages = response.json()['messages']

    assert response.status_code == 200
    assert len(messages) == len(new_chat.chat.messages)
    for idx, message in enumerate(messages):
        assert new_chat.chat.messages[idx].content == message['content']
        assert new_chat.chat.messages[idx].sender == message['sender']
