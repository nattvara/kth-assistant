from enum import Enum


class IndexType(Enum):

    NO_INDEX = 'no_index'

    FULL_TEXT_SEARCH = 'full_text_search'

    VECTOR_SEARCH_SALESFORCE_SFR_EMBEDDING_MISTRAL = 'vector_search:Salesforce/SFR-Embedding-Mistral'

    VECTOR_SEARCH_OPENAI_TEXT_EMBEDDING_3_LARGE = 'vector_search:openai/text-embedding-3-large'


enum_dict = {enum.value: enum for enum in IndexType}


def get_enum_from_enum_name(enum_name: str):
    # Returns the enum from a name, e.g. NO_INDEX
    model_enum = IndexType[enum_name]
    return model_enum


def get_enum_from_enum_value(value: str):
    # Returns the enum from an enum's value, e.g. no_index
    return enum_dict.get(value, None)
