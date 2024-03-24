import warnings

import peewee

from . import BaseModel, Snapshot

# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings(
    "ignore",
    message='"db_table" has been deprecated in favor of "table_name" for Models.',
    category=DeprecationWarning,
    module='peewee'
)


class Url(BaseModel):
    class Meta:
        db_table = 'urls'
        table_name = 'urls'

    class States:
        UNVISITED = 'unvisited'
        VISITED = 'visited'
        CRAWLING = 'crawling'
        FAILED = 'failed'

    id = peewee.AutoField()
    snapshot = peewee.ForeignKeyField(Snapshot, null=False, backref='urls', on_delete='CASCADE')
    state = peewee.CharField(null=False, index=True, default=States.UNVISITED)
    href = peewee.CharField(max_length=1024, null=False)
    root = peewee.BooleanField(null=False, index=True, default=False)
