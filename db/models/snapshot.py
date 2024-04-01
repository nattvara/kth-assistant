import warnings

import peewee

from . import BaseModel, Course

# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings(
    "ignore",
    message='"db_table" has been deprecated in favor of "table_name" for Models.',
    category=DeprecationWarning,
    module='peewee'
)


class Snapshot(BaseModel):
    class Meta:
        db_table = 'snapshots'
        table_name = 'snapshots'

    id = peewee.AutoField()
    course = peewee.ForeignKeyField(Course, null=False, backref='snapshots', on_delete='CASCADE')
