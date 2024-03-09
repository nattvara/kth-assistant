import asyncio

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

from .sampling_strategies import top_k_sampling, top_p_sampling, top_k_and_p_sampling
from config.settings import get_settings
from .config import Params


def load_hf_model(model_path: str, device: str) -> (AutoModelForCausalLM, AutoTokenizer):
    tokenizer = AutoTokenizer.from_pretrained(model_path, token=get_settings().HUGGINGFACE_ACCESS_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, token=get_settings().HUGGINGFACE_ACCESS_TOKEN)

    model.to(device)

    return model, tokenizer


def generate_text(
        model: AutoModelForCausalLM,
        tokenizer: AutoTokenizer,
        device: str,
        params: Params,
        prompt: str,
) -> str:
    output = ''
    generator = generate_text_streaming(model, tokenizer, device, params, prompt)
    for index, token in enumerate(generator):
        output += token
    return output


async def generate_text_streaming(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    device: str,
    params: Params,
    prompt: str,
) -> str:
    prompt = params.system_prompt + prompt

    input_ids = _initialize_prompt(tokenizer, prompt)
    output_token_ids = []
    max_src_len = params.context_length - params.max_new_tokens - 8
    input_ids = input_ids[-max_src_len:]

    past_key_values = None
    generated_text = ""
    with torch.no_grad():
        for i in range(params.max_new_tokens):
            out, past_key_values = _generate_output(model, input_ids, device, i, past_key_values)
            token_id = _select_token(out.logits[0][-1], params)

            output_token_ids.append(token_id)
            input_ids = [token_id]

            current_text = tokenizer.decode(output_token_ids, skip_special_tokens=True)
            new_text = current_text[len(generated_text):]
            generated_text = current_text

            if should_stop_generating(output_token_ids, tokenizer, params, token_id):
                break

            # This call to asyncio.sleep is a non-blocking call that immediately yields control back to the event loop.
            # This allows it to manage other tasks. The sleep time is 0, which might seem pointless, however, it serves
            # as a checkpoint where the event loop can decide to run other pending tasks, such as I/O ops. Before
            # resuming the coroutine that yielded. Since the generation of text is very time-consuming, this will
            # interfere with other tasks if it's running inside the event loop. This will be the case when it's
            # streaming the result over a websocket. Adding this sleep call ensures the websocket connection
            # remains open and doesn't crash.
            await asyncio.sleep(0)

            yield new_text


def _initialize_prompt(tokenizer: AutoTokenizer, prompt: str) -> list:
    input_ids = tokenizer(prompt).input_ids
    return input_ids


def _generate_output(
    model: AutoModelForCausalLM,
    input_ids: list,
    device: str,
    iteration: int,
    past_key_values
) -> tuple:
    if iteration == 0:
        out = model(input_ids=torch.as_tensor([input_ids], device=device), use_cache=True)
    else:
        out = model(input_ids=torch.as_tensor([[input_ids[-1]]], device=device), use_cache=True, past_key_values=past_key_values)
    return out, out.past_key_values


def _select_token(logits: torch.Tensor, params: Params) -> int:
    if params.temperature < 1e-4:
        token_id = int(torch.argmax(logits))
    else:
        probabilities = torch.softmax(logits / params.temperature, dim=-1)
        if params.enable_top_k_filter and params.enable_top_p_filter:
            token_id = top_k_and_p_sampling(logits, params.top_k_limit, params.top_p_threshold)
        elif params.enable_top_k_filter:
            token_id = top_k_sampling(logits, params.top_k_limit)
        elif params.enable_top_p_filter:
            token_id = top_p_sampling(logits, params.top_p_threshold)
        else:
            token_id = int(torch.multinomial(probabilities, num_samples=1))
    return token_id


def should_stop_generating(
    output_token_ids: list,
    tokenizer: AutoTokenizer,
    params: Params,
    token_id: int
) -> bool:
    if token_id in [tokenizer.eos_token_id]:
        return True
    if params.stop_strings:
        output = tokenizer.decode(output_token_ids, skip_special_tokens=True)
        if any(stop_str in output for stop_str in params.stop_strings):
            return True
    return False
