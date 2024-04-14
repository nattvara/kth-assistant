
def find_chat_by_id(chat_id: str):
    from db.models.chat import Chat
    return Chat.select().filter(Chat.public_id == chat_id).first()


def count_chats_with_session(session_id: int):
    from db.models.chat import Chat
    return Chat.select().filter(Chat.session == session_id).count()
