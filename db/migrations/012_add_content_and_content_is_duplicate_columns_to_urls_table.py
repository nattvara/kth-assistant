from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.models import Url, Content


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Url, 'content_id'):
        content_field = pw.ForeignKeyField(Content, null=True, backref='urls', on_delete='CASCADE')
        migrator.add_fields(Url, content=content_field)

    if not column_exists(Url, 'content_is_duplicate'):
        content_is_duplicate_field = pw.BooleanField(null=False, index=True, default=False)
        migrator.add_fields(Url, content_is_duplicate=content_is_duplicate_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing fields with indexes doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Url, 'content', cascade=True)
        migrator.remove_fields(Url, 'content_is_duplicate', cascade=True)
