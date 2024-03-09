from enum import Enum


class LLMModel(Enum):

    # https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
    MISTRAL_7B_INSTRUCT = 'mistralai/Mistral-7B-Instruct-v0.2'

    # https://huggingface.co/google/gemma-7b
    GOOGLE_GEMMA_7B = 'google/gemma-7b'

    # https://huggingface.co/tiiuae/falcon-7b
    FALCON_7B = 'tiiuae/falcon-7b'


enum_dict = {enum.value: enum for enum in LLMModel}


def get_enum_from_enum_name(enum_name: str):
    # Returns the enum from a name, e.g. MISTRAL_7B_INSTRUCT
    model_enum = LLMModel[enum_name]
    return model_enum


def get_enum_from_enum_value(value: str):
    # Returns the enum from an enum's value, e.g. mistralai/Mistral-7B-Instruct-v0.2
    return enum_dict.get(value, None)
