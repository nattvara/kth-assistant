from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.custom_fields import EmbeddingField
from db.models import PromptHandle


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(PromptHandle, 'embedding'):
        embedding_field = EmbeddingField(null=True)
        migrator.add_fields(PromptHandle, embedding=embedding_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(PromptHandle, 'embedding', cascade=True)
