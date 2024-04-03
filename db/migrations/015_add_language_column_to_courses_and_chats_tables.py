from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.models import Course, Chat


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Course, 'language'):
        language_field = pw.CharField(null=False, max_length=4, default='en')
        migrator.add_fields(Course, language=language_field)

    if not column_exists(Chat, 'language'):
        language_field = pw.CharField(null=False, max_length=4, default='en')
        migrator.add_fields(Chat, language=language_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing fields with indexes doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Course, 'language', cascade=True)
        migrator.remove_fields(Chat, 'language', cascade=True)
