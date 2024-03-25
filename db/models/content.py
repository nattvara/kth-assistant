import hashlib
import warnings

import peewee

from . import BaseModel

# Suppress specific DeprecationWarning about db_table, this is needed for migrations to work
warnings.filterwarnings(
    "ignore",
    message='"db_table" has been deprecated in favor of "table_name" for Models.',
    category=DeprecationWarning,
    module='peewee'
)


class Content(BaseModel):
    class Meta:
        db_table = 'content'
        table_name = 'content'

    id = peewee.AutoField()
    sha = peewee.CharField(null=False, index=True)
    name = peewee.CharField(null=True)
    text = peewee.TextField(null=False)

    def make_sha(self):
        if self.text is None:
            raise ValueError("cannot generate sha if text is not defined")

        return hashlib.sha256(str(self.text).encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        self.sha = self.make_sha()
        return super(Content, self).save(*args, **kwargs)
