"""
Here are various sampling methods used in the text generation. These functions used to determine the next token to
be generated during the text creation process. Each function implements a different sampling strategy:

- top_k_sampling:   selects the next token from the top K most likely tokens, as determined by the model's output.
- top_p_sampling:   implements nucleus sampling, tokens are selected from a subset that cumulatively holds a probability
                    mass of P.
- top_k_p_sampling: hybrid approach that combines top-k and top-p sampling methods to produce the best choice for the
                    next token.
"""

from torch import Tensor
import torch


def top_k_sampling(logits: Tensor, k: int) -> int:
    top_k_values, top_k_indices = _get_top_k(logits, k)
    probabilities = torch.softmax(top_k_values, dim=-1)
    choice = torch.multinomial(probabilities, num_samples=1)
    token_id = int(top_k_indices[choice])
    return token_id


def top_p_sampling(logits: Tensor, p: float) -> int:
    logits = _apply_top_probability_mask_to_logits(logits, p)
    probabilities = torch.softmax(logits, dim=-1)
    token_id = int(torch.multinomial(probabilities, num_samples=1))
    return token_id


def top_k_and_p_sampling(logits: Tensor, k: int, p: float) -> int:
    top_k_values, top_k_indices = _get_top_k(logits, k)
    top_k_values = _apply_top_probability_mask_to_top_k_logits(top_k_values, p, top_k_values.device)
    probabilities = torch.softmax(top_k_values, dim=-1)
    choice = torch.multinomial(probabilities, num_samples=1)
    token_id = int(top_k_indices[choice])
    return token_id


def _get_top_k(logits: Tensor, k: int) -> (Tensor, Tensor):
    return torch.topk(logits, k)


def _apply_top_probability_mask_to_logits(logits: Tensor, p: float) -> Tensor:
    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
    cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
    mask = cumulative_probs > p
    mask[..., 1:] = mask[..., :-1].clone()
    mask[..., 0] = 0
    logits[sorted_indices] = torch.where(mask, torch.tensor(-1e10, dtype=logits.dtype), sorted_logits)
    return logits


def _apply_top_probability_mask_to_top_k_logits(top_k_values: Tensor, p: float, device: torch.device) -> Tensor:
    sorted_logits, sorted_indices = torch.sort(top_k_values, descending=True)
    cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
    mask = cumulative_probs > p
    mask[..., 1:] = mask[..., :-1].clone()
    mask[..., 0] = 0
    neg_inf_tensor = torch.tensor(-1e10, dtype=top_k_values.dtype).to(device)
    top_k_values[sorted_indices] = torch.where(mask, neg_inf_tensor, sorted_logits)
    return top_k_values
