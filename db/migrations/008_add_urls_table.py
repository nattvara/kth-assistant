from peewee_migrate import Migrator
import peewee as pw


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # this migration is broken
    pass


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # this migration is broken
    pass
