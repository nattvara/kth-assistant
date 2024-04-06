import warnings
import uuid

import peewee

from . import BaseModel, FaqSnapshot

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


class Faq(BaseModel):
    class Meta:
        db_table = 'faqs'
        table_name = 'faqs'

    id = peewee.AutoField()
    faq_id = peewee.CharField(null=False, index=True, unique=True, default=generate_public_id)
    snapshot = peewee.ForeignKeyField(FaqSnapshot, null=False, backref='faqs', on_delete='CASCADE')
    question = peewee.TextField(null=True)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'faq_id': self.faq_id,
            'question': self.question,
        }
