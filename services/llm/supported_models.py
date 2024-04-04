from enum import Enum


class LLMModel(Enum):

    # https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
    MISTRAL_7B_INSTRUCT = 'mistralai/Mistral-7B-Instruct-v0.2'

    # https://huggingface.co/google/gemma-7b
    GOOGLE_GEMMA_7B = 'google/gemma-7b'

    # https://huggingface.co/tiiuae/falcon-7b
    FALCON_7B = 'tiiuae/falcon-7b'

    # https://github.com/openai/openai-python
    OPENAI_GPT4 = 'openai/gpt4'

    # https://huggingface.co/Salesforce/SFR-Embedding-Mistral
    SALESFORCE_SFR_EMBEDDING_MISTRAL = 'Salesforce/SFR-Embedding-Mistral'

    # https://huggingface.co/Salesforce/SFR-Embedding-Mistral
    INTFLOAT_MULTILINGUAL_E5_LARGE_INSTRUCT = 'intfloat/multilingual-e5-large-instruct'

    # https://platform.openai.com/docs/guides/embeddings/
    OPENAI_TEXT_EMBEDDING_3_LARGE = 'openai/text-embedding-3-large'


enum_dict = {enum.value: enum for enum in LLMModel}

# These models are embedding models, this map maps them to their name in
# the opensearch index
EMBEDDING_MODELS = {
    LLMModel.SALESFORCE_SFR_EMBEDDING_MISTRAL: 'sfr_embedding_mistral',
    LLMModel.INTFLOAT_MULTILINGUAL_E5_LARGE_INSTRUCT: 'intfloat_me5li',
    LLMModel.OPENAI_TEXT_EMBEDDING_3_LARGE: 'text_embedding_3_large',
}

# https://huggingface.co/spaces/mteb/leaderboard
EMBEDDING_MODELS_DIMENSIONS = {
    LLMModel.SALESFORCE_SFR_EMBEDDING_MISTRAL: 4096,
    LLMModel.INTFLOAT_MULTILINGUAL_E5_LARGE_INSTRUCT: 1024,
    LLMModel.OPENAI_TEXT_EMBEDDING_3_LARGE: 3072,
}


def get_enum_from_enum_name(enum_name: str):
    # Returns the enum from a name, e.g. MISTRAL_7B_INSTRUCT
    model_enum = LLMModel[enum_name]
    return model_enum


def get_enum_from_enum_value(value: str):
    # Returns the enum from an enum's value, e.g. mistralai/Mistral-7B-Instruct-v0.2
    return enum_dict.get(value, None)
