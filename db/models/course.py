import warnings
import secrets
import string

import peewee

from db.custom_fields import ExtraUrlsField
from . import BaseModel

# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings(
    "ignore",
    message='"db_table" has been deprecated in favor of "table_name" for Models.',
    category=DeprecationWarning,
    module='peewee'
)


def _generate_admin_token():
    alphabet = string.ascii_letters + string.digits
    secure_string = ''.join(secrets.choice(alphabet) for _ in range(42))
    return secure_string


class Course(BaseModel):
    class Meta:
        db_table = 'courses'
        table_name = 'courses'

    class Language:
        ENGLISH = 'en'
        SWEDISH = 'sv'

    canvas_id = peewee.CharField(null=False, index=True, unique=True)
    snapshot_lifetime_in_mins = peewee.IntegerField(null=False, default=180)
    max_allowed_crawl_distance = peewee.IntegerField(null=False, default=2)
    language = peewee.CharField(null=False, max_length=4, default='en')
    name = peewee.CharField(null=False, default='Untitled Course Room')
    description = peewee.TextField(null=False, default='Course room has not got any description')
    admin_token = peewee.CharField(null=False, index=True, unique=True, default=_generate_admin_token)
    extra_urls = ExtraUrlsField(null=False, default=[])
