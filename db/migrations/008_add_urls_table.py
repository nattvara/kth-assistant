from peewee_migrate import Migrator
import peewee as pw

from db.connection import db
from db.models import Url


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.create_tables([Url])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.drop_tables([Url])
