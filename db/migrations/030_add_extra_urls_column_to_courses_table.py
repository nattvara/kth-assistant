from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.custom_fields import ExtraUrlsField
from db.models import Course


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Course, 'extra_urls'):
        extra_urls_field = ExtraUrlsField(null=False, default=[])
        migrator.add_fields(Course, extra_urls=extra_urls_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Course, 'extra_urls', cascade=True)
