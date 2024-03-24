from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.models import Course


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Course, 'snapshot_lifetime_in_mins'):
        snapshot_lifetime_in_mins_field = pw.IntegerField(null=False, default=180)
        migrator.add_fields(Course, snapshot_lifetime_in_mins=snapshot_lifetime_in_mins_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing fields with indexes doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Course, 'snapshot_lifetime_in_mins', cascade=True)
