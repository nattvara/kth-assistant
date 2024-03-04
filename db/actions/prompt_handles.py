
def find_prompt_handle_by_websocket_uri(uri: str):
    from db.models.prompt_handle import PromptHandle
    return PromptHandle.select().filter(PromptHandle.websocket_uri == uri).first()
