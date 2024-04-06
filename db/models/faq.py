import warnings

import peewee

from . import BaseModel, FaqSnapshot

# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings(
    "ignore",
    message='"db_table" has been deprecated in favor of "table_name" for Models.',
    category=DeprecationWarning,
    module='peewee'
)


class Faq(BaseModel):
    class Meta:
        db_table = 'faqs'
        table_name = 'faqs'

    id = peewee.AutoField()
    snapshot = peewee.ForeignKeyField(FaqSnapshot, null=False, backref='faqs', on_delete='CASCADE')
    question = peewee.TextField(null=True)
