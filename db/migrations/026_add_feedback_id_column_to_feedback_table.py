from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.models import Feedback
from db.models.feedback import _generate_id


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Feedback, 'feedback_id'):
        feedback_id_field = pw.CharField(null=False, index=True, unique=True, default=_generate_id)
        migrator.add_fields(Feedback, feedback_id=feedback_id_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing fields doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Feedback, 'feedback_id', cascade=True)
