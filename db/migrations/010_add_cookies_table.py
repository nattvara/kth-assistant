from peewee_migrate import Migrator
import peewee as pw

from db.connection import db
from db.models import Cookie


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.create_tables([Cookie])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.drop_tables([Cookie])
