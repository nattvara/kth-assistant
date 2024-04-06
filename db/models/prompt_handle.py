import warnings
import secrets
import string

import peewee

from db.custom_fields import ModelParamsField, ModelNameField, EmbeddingField
from . import BaseModel

# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings(
    "ignore",
    message='"db_table" has been deprecated in favor of "table_name" for Models.',
    category=DeprecationWarning,
    module='peewee'
)


def generate_websocket_uri():
    alphabet = string.ascii_letters + string.digits
    secure_string = ''.join(secrets.choice(alphabet) for _ in range(128))
    return f"/ws/{secure_string}"


class PromptHandle(BaseModel):
    class Meta:
        db_table = 'prompt_handles'
        table_name = 'prompt_handles'

    class States:
        PENDING = 'pending'
        FINISHED = 'finished'
        IN_PROGRESS = 'in_progress'

    id = peewee.AutoField()
    state = peewee.CharField(null=False, index=True, default=States.PENDING)
    websocket_uri = peewee.TextField(null=False, index=True, default=generate_websocket_uri)
    prompt = peewee.TextField(null=False)
    llm_model_name = ModelNameField(null=False, index=True)
    llm_model_params = ModelParamsField(null=True)
    time_spent_pending_ms = peewee.IntegerField(null=True, default=None)
    response = peewee.TextField(null=True)
    response_length = peewee.IntegerField(null=True, default=None)
    response_time_taken_s = peewee.IntegerField(null=True, default=None)
    embedding = EmbeddingField(null=True)
