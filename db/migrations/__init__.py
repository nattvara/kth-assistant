from peewee_migrate import Router
import sys
import os

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
