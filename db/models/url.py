import warnings
import hashlib

import peewee

from . import BaseModel, Snapshot, Content

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
    href_sha = peewee.CharField(null=False, index=True)
    root = peewee.BooleanField(null=False, index=True, default=False)
    distance = peewee.IntegerField(null=False)
    is_download = peewee.BooleanField(null=False, index=True, default=False)
    response_was_ok = peewee.BooleanField(null=False, index=True, default=False)
    content = peewee.ForeignKeyField(Content, null=True, backref='urls', on_delete='CASCADE')
    content_is_duplicate = peewee.BooleanField(null=False, index=True, default=False)

    @staticmethod
    def make_href_sha(href: str):
        if href is None:
            raise ValueError("cannot generate href_sha if href is not defined")

        return hashlib.sha256(str(href).encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        self.href_sha = Url.make_href_sha(str(self.href))
        return super(Url, self).save(*args, **kwargs)
