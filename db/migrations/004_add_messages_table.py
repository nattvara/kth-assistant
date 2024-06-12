from peewee_migrate import Migrator
import peewee as pw

from db.models import Message, Faq, FaqSnapshot
from db.connection import db


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.create_tables([Message, Faq, FaqSnapshot])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    db.drop_tables([Message, Faq, FaqSnapshot])
