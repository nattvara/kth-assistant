
def all_messages_in_chat(chat_id: int):
    from db.models.message import Message
    return Message.select().where(Message.chat == chat_id).order_by(Message.created_at.asc())


def find_message_by_chat_private_id_and_message_public_id(chat_id: int, message_id: str):
    from db.models.message import Message
    return Message.select().filter(
        Message.chat == chat_id
    ).filter(
        Message.message_id == message_id
    ).first()
