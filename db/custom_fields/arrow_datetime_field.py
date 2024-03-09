from playhouse.sqlite_ext import DateTimeField
import arrow


class ArrowDateTimeField(DateTimeField):
    def python_value(self, value):
        date_val = super().python_value(value)
        if date_val:
            return arrow.get(date_val)
        return None

    def db_value(self, value):
        if isinstance(value, arrow.Arrow):
            return value.datetime
        return super().db_value(value)
