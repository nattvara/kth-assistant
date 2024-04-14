import warnings
import uuid

import peewee

from . import BaseModel, Chat, PromptHandle, Faq

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
        FEEDBACK = 'feedback'

    class States:
        """
        - a message is ready when it can be shown on screen (such as completely finished, or the content
          of the message is being streamed into the chat
        - a message is pending if the system is gathering data to generate the message,
          such as gathering data from an index
        """
        READY = 'ready'
        PENDING = 'pending'

    id = peewee.AutoField()
    message_id = peewee.CharField(null=False, index=True, unique=True, default=generate_public_id)
    chat = peewee.ForeignKeyField(Chat, null=False, backref='messages', on_delete='CASCADE')
    sender = peewee.CharField(null=False)
    state = peewee.CharField(null=False, index=True, default=States.READY)
    content = peewee.TextField(null=True)
    prompt_handle = peewee.ForeignKeyField(PromptHandle, null=True, backref='messages', on_delete='CASCADE')
    faq = peewee.ForeignKeyField(Faq, null=True, backref='messages', on_delete='CASCADE')
