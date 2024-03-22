from services.chat.chat_service import ChatService


def test_chat_service_can_produce_message_for_chat_without_any_index(mocker, new_chat):
    mock_prompt = mocker.patch('services.llm.prompts.prompt_make_next_ai_message')
    new_chat.add_some_messages()
    messages = [message for message in new_chat.chat.messages]

    message = ChatService.request_next_message(new_chat.chat)

    mock_prompt.assert_called_once()
    mock_prompt.assert_called_with(messages)
    assert len(new_chat.chat.messages) == len(messages) + 1
