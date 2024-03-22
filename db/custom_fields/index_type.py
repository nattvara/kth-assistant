from playhouse.sqlite_ext import CharField

from services.index.supported_indices import get_enum_from_enum_value, IndexType


class IndexTypeField(CharField):

    def db_value(self, value: IndexType) -> str:
        return value.value

    def python_value(self, value: str) -> IndexType:
        return get_enum_from_enum_value(value)
