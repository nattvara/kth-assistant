from peewee_migrate import Migrator
import peewee as pw

from db.models import Session
from db.connection import db


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.create_tables([Session])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.drop_tables([Session])
