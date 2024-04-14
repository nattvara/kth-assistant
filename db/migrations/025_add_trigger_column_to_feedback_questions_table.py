from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.models import FeedbackQuestion


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(FeedbackQuestion, 'trigger'):
        trigger_field = pw.CharField(null=False, index=True, default="no_trigger")
        migrator.add_fields(FeedbackQuestion, trigger=trigger_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing fields doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(FeedbackQuestion, 'trigger', cascade=True)
