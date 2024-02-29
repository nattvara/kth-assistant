from peewee_migrate import Router

from db.migrations import MIGRATIONS_DIR
from db.models import all_models
from db.connection import db
from config.logger import log
from tests.assertions import assert_table_count


def test_all_migrations_can_be_applied():
    db.drop_tables(all_models)

    router = Router(db, migrate_dir=MIGRATIONS_DIR, logger=log())
    router.run()

    assert_table_count(2)


def test_all_migrations_can_be_rolled_back():
    db.drop_tables(all_models)

    router = Router(db, migrate_dir=MIGRATIONS_DIR, logger=log())
    router.rollback()

    assert_table_count(1)  # migrations table will be only table left
