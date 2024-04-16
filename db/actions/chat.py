
def find_chat_by_id(chat_id: str):
    from db.models.chat import Chat
    return Chat.select().filter(Chat.public_id == chat_id).first()


def count_chats_with_session(session_id: int) -> int:
    from db.models.chat import Chat
    from db.models.message import Message
    from peewee import fn

    # Only count chats that have at least one message
    query = (Chat
             .select(fn.COUNT(Chat.id).alias('chat_count'))
             .join(Message, on=(Chat.id == Message.chat))
             .where(Chat.session == session_id)
             .group_by(Chat.id))

    count = 0
    for _ in query:
        count += 1

    return count
