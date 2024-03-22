from peewee_migrate import Migrator
import peewee as pw

from services.index.supported_indices import IndexType
from db.migrations import column_exists, is_sqlite
from db.custom_fields import IndexTypeField
from db.models import Chat


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Chat, 'index_type'):
        index_type_field = IndexTypeField(null=False, index=True, default=IndexType.NO_INDEX)
        migrator.add_fields(Chat, index_type=index_type_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing fields with indexes doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Chat, 'index_type', cascade=True)
