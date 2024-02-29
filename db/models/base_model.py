import peewee
import arrow

from db.connection import db
from db.custom_fields import ArrowDateTimeField


class BaseModel(peewee.Model):
    created_at = ArrowDateTimeField(default=arrow.utcnow, null=False)
    modified_at = ArrowDateTimeField(default=arrow.utcnow, null=False)

    class Meta:
        database = db

    class Config:
        orm_mode = True

    def save(self, *args, **kwargs):
        self.modified_at = arrow.utcnow()
        return super(BaseModel, self).save(*args, **kwargs)
