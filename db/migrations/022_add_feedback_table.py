from peewee_migrate import Migrator
import peewee as pw

from db.models import Feedback
from db.connection import db


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.create_tables([Feedback])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.drop_tables([Feedback])
