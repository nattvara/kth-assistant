from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.models import Course


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Course, 'name'):
        name_field = pw.CharField(null=False, default='Untitled Course Room')
        migrator.add_fields(Course, name=name_field)

    if not column_exists(Course, 'description'):
        description_field = pw.TextField(null=False, default='Course room has not got any description')
        migrator.add_fields(Course, description=description_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing fields with indexes doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Course, 'name', cascade=True)
        migrator.remove_fields(Course, 'description', cascade=True)
