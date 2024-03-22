from typing import Optional, Union
import json

from playhouse.sqlite_ext import JSONField

from llms.config import Params


class ModelParamsField(JSONField):

    def db_value(self, value: Params) -> str:
        if value is not None:
            return json.dumps(value.__dict__)
        return super().db_value(value)

    def python_value(self, value: Union[str, dict]) -> Optional[Params]:
        if value is not None:
            if isinstance(value, dict):
                return Params(**value)

            params_dict = json.loads(value)
            return Params(**params_dict)

        return None
