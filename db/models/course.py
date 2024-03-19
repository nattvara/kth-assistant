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


class Course(BaseModel):
    class Meta:
        db_table = 'courses'
        table_name = 'courses'

    canvas_id = peewee.CharField(null=False, index=True, unique=True)
