import warnings
import peewee

from . import BaseModel


# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings("ignore", message='"db_table" has been deprecated in favor of "table_name" for Models.', category=DeprecationWarning, module='peewee')


class PromptHandle(BaseModel):
    class Meta:
        db_table = 'prompt_handles'
        table_name = 'prompt_handles'

    class States:
        PENDING = 'pending'
        FINISHED = 'finished'

    state = peewee.CharField(null=False, index=True, default=States.PENDING)
    prompt = peewee.TextField(null=True)
