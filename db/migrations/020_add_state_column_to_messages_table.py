from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.models import Message


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Message, 'state'):
        state_field = pw.CharField(null=False, index=True, default=Message.States.READY)
        migrator.add_fields(Message, state=state_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing fields with indexes doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Message, 'state', cascade=True)
