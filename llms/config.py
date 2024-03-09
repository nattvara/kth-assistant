from typing import Optional, List


class Params:
    def __init__(
        self,
        temperature: float = 0.7,
        max_new_tokens: int = 1024,
        context_length: int = 8096,
        enable_top_k_filter: bool = True,
        top_k_limit: int = 50,
        enable_top_p_filter: bool = True,
        top_p_threshold: float = 0.7,
        stop_strings: Optional[List[str]] = None,
        system_prompt: str = '',
    ):
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.context_length = context_length
        self.enable_top_k_filter = enable_top_k_filter
        self.top_k_limit = top_k_limit
        self.enable_top_p_filter = enable_top_p_filter
        self.top_p_threshold = top_p_threshold
        self.stop_strings = stop_strings if stop_strings is not None else []
        self.system_prompt = system_prompt
