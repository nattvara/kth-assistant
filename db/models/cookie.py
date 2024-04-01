import warnings

import peewee

from . import BaseModel

# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings(
    "ignore",
    message='"db_table" has been deprecated in favor of "table_name" for Models.',
    category=DeprecationWarning,
    module='peewee'
)


class Cookie(BaseModel):
    class Meta:
        db_table = 'cookies'
        table_name = 'cookies'

    identifier = peewee.CharField(null=False, unique=True, primary_key=True)
    value = peewee.TextField(null=False)
