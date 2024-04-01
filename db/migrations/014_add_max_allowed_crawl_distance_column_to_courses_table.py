from peewee_migrate import Migrator
import peewee as pw

from db.migrations import column_exists, is_sqlite
from db.models import Course


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    if not column_exists(Course, 'max_allowed_crawl_distance'):
        max_allowed_crawl_distance_field = pw.IntegerField(null=False, default=2)
        migrator.add_fields(Course, max_allowed_crawl_distance=max_allowed_crawl_distance_field)


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    # ignore this operation on sqlite, as removing fields with indexes doesn't work
    if not is_sqlite(database):
        migrator.remove_fields(Course, 'max_allowed_crawl_distance', cascade=True)
