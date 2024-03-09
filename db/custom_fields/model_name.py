from playhouse.sqlite_ext import CharField

from services.llm.supported_models import get_enum_from_enum_value, LLMModel


class ModelNameField(CharField):

    def db_value(self, value: LLMModel) -> str:
        return value.value

    def python_value(self, value: str) -> LLMModel:
        return get_enum_from_enum_value(value)
