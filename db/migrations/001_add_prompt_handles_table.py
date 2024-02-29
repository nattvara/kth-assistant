from peewee_migrate import Migrator
import peewee as pw

from db.models import PromptHandle
from db.connection import db


try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.create_tables([PromptHandle])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.drop_tables([PromptHandle])
