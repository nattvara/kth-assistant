import warnings

import peewee

from db.custom_fields import ModelNameField, IndexTypeField
from . import BaseModel

# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings(
    "ignore",
    message='"db_table" has been deprecated in favor of "table_name" for Models.',
    category=DeprecationWarning,
    module='peewee'
)


class ChatConfig(BaseModel):
    class Meta:
        db_table = 'chat_configs'
        table_name = 'chat_configs'

    id = peewee.AutoField()
    is_active = peewee.BooleanField(null=False, default=True)
    llm_model_name = ModelNameField(null=False, index=True)
    index_type = IndexTypeField(null=False, index=True)
