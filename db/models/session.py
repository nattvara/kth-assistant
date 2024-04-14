import warnings
import uuid

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


def generate_id() -> str:
    uuid5 = uuid.uuid4()
    return str(uuid5)


class Session(BaseModel):
    class Meta:
        db_table = 'sessions'
        table_name = 'sessions'

    id = peewee.AutoField()
    is_valid = peewee.BooleanField(default=True)
    public_id = peewee.CharField(null=False, index=True, unique=True, default=generate_id)
    consent = peewee.BooleanField(default=False)
    default_llm_model_name = ModelNameField(null=False, index=True)
    default_index_type = IndexTypeField(null=False, index=True)
