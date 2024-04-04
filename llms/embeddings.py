from typing import List

from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F
from torch import Tensor, nn
import torch

from config.settings import get_settings


def load_hf_embedding_model(model_path: str, device: str) -> (nn.Module, AutoTokenizer):
    tokenizer = AutoTokenizer.from_pretrained(model_path, token=get_settings().HUGGINGFACE_ACCESS_TOKEN)
    model = AutoModel.from_pretrained(model_path, token=get_settings().HUGGINGFACE_ACCESS_TOKEN)

    model.to(device)

    return model, tokenizer


async def compute_embedding(model: nn.Module, tokeniser: AutoTokenizer, text: str) -> List[float]:
    tokenised_inputs = _tokenise_inputs(tokeniser, [text])
    model_embeddings = _compute_model_embeddings(model, tokenised_inputs)
    pooled_embeddings = _last_token_pool(model_embeddings, tokenised_inputs['attention_mask'])
    normalised_embeddings = _normalise_embeddings(pooled_embeddings)
    return normalised_embeddings[0].cpu().numpy().tolist()


def _tokenise_inputs(tokeniser: AutoTokenizer, input_texts: list[str], max_length: int = 8192) -> dict:
    return tokeniser(input_texts, max_length=max_length, padding=True, truncation=True, return_tensors='pt')


def _compute_model_embeddings(model: nn.Module, tokenised_inputs: dict) -> Tensor:
    with torch.no_grad():
        outputs = model(**tokenised_inputs)
    return outputs.last_hidden_state


def _last_token_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
    if left_padding:
        return last_hidden_states[:, -1]
    sequence_lengths = attention_mask.sum(dim=1) - 1
    batch_size = last_hidden_states.shape[0]
    return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]


def _normalise_embeddings(embeddings: Tensor) -> Tensor:
    return F.normalize(embeddings, p=2, dim=1)
