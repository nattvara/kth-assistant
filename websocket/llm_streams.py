import asyncio

from redis.asyncio.client import PubSub
from starlette.websockets import WebSocketDisconnect
from redis.asyncio import Redis
from fastapi import WebSocket
import arrow

import config.settings as settings
from config.logger import log


async def handle_websocket_connection_between_worker_and_requester(
        websocket: WebSocket,
        session_id: str,
        redis: Redis
):
    """
    Handle the communication between workers and requesters over a websocket.

    The websocket should be one-to-one (although it technically supports many-to-many),
    i.e. one requester is listening on the websocket to messages sent by one worker.
    There is no enforcement of this in the protocol below.

    :param websocket: The websocket over which the communication happens
    :param session_id: The id of the session. Given a websocket uri "/ws/{session_id}"
    :param redis: A redis connection to push and read messages from.
    :return: None
    """
    pubsub = redis.pubsub()
    await pubsub.subscribe(session_id)
    last_activity_time = arrow.now()

    try:
        await asyncio.gather(
            listen_to_redis(pubsub, websocket),
            listen_to_websocket(websocket, redis, session_id),
            check_timeout(websocket, last_activity_time, settings.get_settings().WEBSOCKET_TIMEOUT_DURATION),
        )
    except WebSocketDisconnect:
        log().debug("WebSocket connection closed")
    finally:
        await pubsub.unsubscribe(session_id)
        await redis.close()
        try:
            await websocket.close()
        except RuntimeError:
            log().debug("WebSocket already closed")


async def listen_to_redis(pubsub: PubSub, websocket: WebSocket):
    async for message in pubsub.listen():
        if message['type'] == 'message':
            await websocket.send_text(message['data'])


async def listen_to_websocket(websocket: WebSocket, redis, session_id: str):
    while True:
        data = await websocket.receive_text()
        await redis.publish(session_id, data)


async def check_timeout(
        websocket: WebSocket,
        last_activity_time: arrow,
        timeout_duration=30
):
    while True:
        await asyncio.sleep(2)
        if (arrow.now() - last_activity_time).total_seconds() > timeout_duration:
            await websocket.close()
            return
