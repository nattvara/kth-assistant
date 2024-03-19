from peewee_migrate import Migrator
import peewee as pw

from db.models import Course, Chat
from db.connection import db


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.create_tables([Course, Chat])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.drop_tables([Course, Chat])
