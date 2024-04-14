from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.models import Session


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Session, 'consent'):
        consent_field = pw.BooleanField(default=False)
        migrator.add_fields(Session, consent=consent_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing fields doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Session, 'consent', cascade=True)
