import warnings
import uuid

import peewee

from db.custom_fields import ModelParamsField, ModelNameField
from . import BaseModel, Course, Session

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
    model_name = ModelNameField(null=False, index=True)