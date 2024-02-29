from db.models import PromptHandle


class LLMService:

    def __init__(self):
        pass

    def dispatch_prompt(self, prompt: str) -> PromptHandle:
        handle = PromptHandle(prompt=prompt)
        handle.save()
        return handle
