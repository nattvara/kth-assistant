from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.custom_fields import CoursesListField
from db.models import Session


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Session, 'admin_courses'):
        admin_courses_field = CoursesListField(null=False, default=[])
        migrator.add_fields(Session, admin_courses=admin_courses_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Session, 'admin_courses', cascade=True)
