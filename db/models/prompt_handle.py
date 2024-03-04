import warnings
import secrets
import string

import peewee

from . import BaseModel


# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings("ignore", message='"db_table" has been deprecated in favor of "table_name" for Models.', category=DeprecationWarning, module='peewee')


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

    state = peewee.CharField(null=False, index=True, default=States.PENDING)
    websocket_uri = peewee.TextField(null=False, index=True, default=generate_websocket_uri)
    prompt = peewee.TextField(null=True)
