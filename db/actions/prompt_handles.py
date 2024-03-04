
def find_prompt_handle_by_websocket_uri(uri: str):
    from db.models.prompt_handle import PromptHandle
    return PromptHandle.select().filter(PromptHandle.websocket_uri == uri).first()


def find_most_recent_pending_handle():
    from db.models.prompt_handle import PromptHandle
    return PromptHandle.select().filter(
        PromptHandle.state == PromptHandle.States.PENDING
    ).order_by(
        PromptHandle.created_at.asc()
    ).first()
