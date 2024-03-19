
def find_chat_by_id(chat_id: str):
    from db.models.chat import Chat
    return Chat.select().filter(Chat.public_id == chat_id).first()
