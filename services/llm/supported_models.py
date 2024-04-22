from enum import Enum

import torch


class LLMModel(Enum):

    # https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
    MISTRAL_7B_INSTRUCT = 'mistralai/Mistral-7B-Instruct-v0.2'

    # https://huggingface.co/google/gemma-7b
    GOOGLE_GEMMA_7B = 'google/gemma-7b'

    # https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct
    META_LLAMA_3_8B_INSTRUCT = 'meta-llama/Meta-Llama-3-8B-Instruct'

    # https://huggingface.co/tiiuae/falcon-7b
    FALCON_7B = 'tiiuae/falcon-7b'

    # https://github.com/openai/openai-python
    OPENAI_GPT4 = 'openai/gpt4'

    # https://huggingface.co/Salesforce/SFR-Embedding-Mistral
    SALESFORCE_SFR_EMBEDDING_MISTRAL = 'Salesforce/SFR-Embedding-Mistral'

    # https://platform.openai.com/docs/guides/embeddings/
    OPENAI_TEXT_EMBEDDING_3_LARGE = 'openai/text-embedding-3-large'


enum_dict = {enum.value: enum for enum in LLMModel}

# These models are embedding models, this map maps them to their name in
# the opensearch index
EMBEDDING_MODELS = {
    LLMModel.SALESFORCE_SFR_EMBEDDING_MISTRAL: 'sfr_embedding_mistral',
    LLMModel.OPENAI_TEXT_EMBEDDING_3_LARGE: 'text_embedding_3_large',
}

# https://huggingface.co/spaces/mteb/leaderboard
EMBEDDING_MODELS_DIMENSIONS = {
    LLMModel.SALESFORCE_SFR_EMBEDDING_MISTRAL: 4096,
    LLMModel.OPENAI_TEXT_EMBEDDING_3_LARGE: 3072,
}

TORCH_DATATYPE_MAP = {
    LLMModel.MISTRAL_7B_INSTRUCT: torch.float16,
    LLMModel.GOOGLE_GEMMA_7B: torch.float16,
    LLMModel.FALCON_7B: torch.float16,
    LLMModel.META_LLAMA_3_8B_INSTRUCT: torch.bfloat16,
}


def get_enum_from_enum_name(enum_name: str):
    # Returns the enum from a name, e.g. MISTRAL_7B_INSTRUCT
    model_enum = LLMModel[enum_name]
    return model_enum


def get_enum_from_enum_value(value: str):
    # Returns the enum from an enum's value, e.g. mistralai/Mistral-7B-Instruct-v0.2
    return enum_dict.get(value, None)
