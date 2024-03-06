from fastapi import APIRouter, WebSocket, HTTPException

from websocket_protocols.llm_streams import handle_websocket_connection_between_worker_and_requester
from db.actions.prompt_handles import find_prompt_handle_by_websocket_uri
from cache.redis import get_redis_connection

router = APIRouter()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    handle = find_prompt_handle_by_websocket_uri(f"/ws/{session_id}")
    if handle is None:
        raise HTTPException(status_code=404)

    await websocket.accept()
    redis = await get_redis_connection()

    await handle_websocket_connection_between_worker_and_requester(websocket, session_id, redis)
