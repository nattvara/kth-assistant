
def all_messages_in_chat(chat_id: int):
    from db.models.message import Message
    return Message.select().where(Message.chat == chat_id).order_by(Message.created_at.asc())
