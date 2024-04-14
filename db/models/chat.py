import warnings
import uuid

import peewee

from db.custom_fields import ModelParamsField, ModelNameField, IndexTypeField
from . import BaseModel, Course, Session

# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings(
    "ignore",
    message='"db_table" has been deprecated in favor of "table_name" for Models.',
    category=DeprecationWarning,
    module='peewee'
)


def generate_id() -> str:
    uuid5 = uuid.uuid4()
    return str(uuid5)


class Chat(BaseModel):
    class Meta:
        db_table = 'chats'
        table_name = 'chats'

    id = peewee.AutoField()
    public_id = peewee.CharField(null=False, index=True, unique=True, default=generate_id)
    course = peewee.ForeignKeyField(Course, null=False, backref='chats', on_delete='CASCADE')
    session = peewee.ForeignKeyField(Session, null=False, backref='sessions', on_delete='CASCADE')
    llm_model_name = ModelNameField(null=False, index=True)
    llm_model_params = ModelParamsField(null=True)
    index_type = IndexTypeField(null=False, index=True)
    language = peewee.CharField(null=False, max_length=4, default='en')

    def get_student_and_assistant_messages(self) -> list:
        out = []

        for message in self.messages:
            if message.sender == message.Sender.STUDENT:
                out.append(message)
            elif message.sender == message.Sender.ASSISTANT:
                out.append(message)

        return out
