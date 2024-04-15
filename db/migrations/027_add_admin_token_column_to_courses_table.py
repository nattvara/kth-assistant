from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.models.course import _generate_admin_token
from db.models import Course


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Course, 'admin_token'):
        admin_token_field = pw.CharField(null=False, index=True, default=_generate_admin_token)
        migrator.add_fields(Course, admin_token=admin_token_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing fields doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Course, 'admin_token', cascade=True)
