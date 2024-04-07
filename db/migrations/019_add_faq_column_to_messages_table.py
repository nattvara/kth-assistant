from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.models import Message, Faq


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Message, 'faq_id'):
        faq_field = pw.ForeignKeyField(Faq, null=True, backref='messages', on_delete='CASCADE')
        migrator.add_fields(Message, faq=faq_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing fields with indexes doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Message, 'faq', cascade=True)
