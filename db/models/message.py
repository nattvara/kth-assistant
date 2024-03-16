import warnings
import uuid

import peewee

from . import BaseModel, Chat

# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings(
    "ignore",
    message='"db_table" has been deprecated in favor of "table_name" for Models.',
    category=DeprecationWarning,
    module='peewee'
)


def generate_public_id() -> str:
    uuid5 = uuid.uuid4()
    return str(uuid5)


class Message(BaseModel):
    class Meta:
        db_table = 'messages'
        table_name = 'messages'

    class Sender:
        STUDENT = 'student'
        ASSISTANT = 'assistant'

    id = peewee.AutoField()
    message_id = peewee.CharField(null=False, index=True, unique=True, default=generate_public_id)
    chat = peewee.ForeignKeyField(Chat, null=False, backref='messages', on_delete='CASCADE')
    sender = peewee.CharField(null=False)
    content = peewee.TextField(null=False)
