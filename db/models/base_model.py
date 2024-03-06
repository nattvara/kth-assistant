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

    def refresh(self):
        model = type(self)
        fields = [getattr(model, field.name) for field in model._meta.fields.values()]
        query = model.select(*fields).where(model.id == self.id)

        latest_instance = query.get()

        for field in fields:
            setattr(self, field.name, getattr(latest_instance, field.name))
