from peewee import fn


def get_random_chat_config():
    from db.models.chat_config import ChatConfig
    return ChatConfig.select().order_by(fn.Random()).first()
