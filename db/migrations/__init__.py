import sys
import os

from playhouse.reflection import Introspector
from peewee_migrate import Router
from peewee import Model
import peewee

from db.connection import db
from config.logger import log

MIGRATIONS_DIR = os.path.dirname(os.path.realpath(__file__))


def create_migration():
    if len(sys.argv) < 2:
        print("Usage: migration_create <migration_name>")
        sys.exit(1)
    get_router().create(sys.argv[1])


def run_migrations():
    get_router().run()


def rollback():
    get_router().rollback()


def get_router():
    return Router(db, migrate_dir=MIGRATIONS_DIR, logger=log())


def column_exists(model: Model, column_name: str) -> bool:
    try:
        introspector = Introspector.from_database(model._meta.database)
        columns = introspector.introspect(model._meta.table_name).columns[model._meta.table_name]
        return column_name in columns
    except TypeError:
        return False


def is_sqlite(database: peewee.Database):
    return isinstance(database, peewee.SqliteDatabase)
