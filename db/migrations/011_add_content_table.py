from peewee_migrate import Migrator
import peewee as pw

from db.connection import db
from db.models import Content


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.create_tables([Content])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.drop_tables([Content])
