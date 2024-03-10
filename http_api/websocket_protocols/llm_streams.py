import asyncio
import uuid

from starlette.websockets import WebSocketDisconnect
from redis.asyncio.client import PubSub
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

    websocket_session = {
        'id': uuid.uuid4(),
        'started_at': arrow.now(),
        'last_activity_time': arrow.now(),
        'write_only': False,  # write-only sessions are for llm workers
        'closed': False,
        'tokens_transmitted': 0
    }

    try:
        await asyncio.gather(
            listen_to_redis(pubsub, websocket, websocket_session),
            listen_to_websocket(websocket, redis, session_id, websocket_session),
            check_timeout(websocket, websocket_session, settings.get_settings().WEBSOCKET_TIMEOUT_DURATION),
        )
    except WebSocketDisconnect:
        log().debug(f"[websocket_id:{websocket_session['id']}] client disconnected from websocket.")
        await close_websocket(websocket, websocket_session)
    finally:
        await pubsub.unsubscribe(session_id)
        await redis.close()
        await close_websocket(websocket, websocket_session)


async def listen_to_redis(pubsub: PubSub, websocket: WebSocket, websocket_session: dict):
    async for message in pubsub.listen():
        if message['type'] == 'message':
            if not websocket_session['write_only']:
                await websocket.send_text(message['data'])
                websocket_session['tokens_transmitted'] += 1

            websocket_session['last_activity_time'] = arrow.now()


async def listen_to_websocket(websocket: WebSocket, redis, session_id: str, websocket_session: dict):
    while True:
        data = await websocket.receive_text()

        if not websocket_session['write_only']:
            log().debug(f"[websocket_id:{websocket_session['id']}] received data "
                        f"from websocket, turning it to write-only")
            websocket_session['write_only'] = True

        websocket_session['tokens_transmitted'] += 1

        await redis.publish(session_id, data)
        websocket_session['last_activity_time'] = arrow.now()


async def check_timeout(websocket: WebSocket, websocket_session: dict, timeout_duration=30):
    while True:
        await asyncio.sleep(1)
        if websocket_session['closed']:
            return await close_websocket(websocket, websocket_session)

        log().debug(f"[websocket_id:{websocket_session['id']}] Transmitted "
                    f"{websocket_session['tokens_transmitted']} tokens over websocket.")

        elapsed_time = (arrow.now() - websocket_session['last_activity_time']).total_seconds()
        log().debug(f"[websocket_id:{websocket_session['id']}] Checking timeout: {elapsed_time} "
                    f"seconds elapsed since last activity.")

        if websocket_session['tokens_transmitted'] == 0 and not websocket_session['write_only']:
            log().info(f"[websocket_id:{websocket_session['id']}] Ignoring timout since no tokens have been "
                       f"transmitted and this is not a write only thread. No worker has picked-up the prompt handle. "
                       f"Waiting for next token.")
            continue

        if elapsed_time > timeout_duration:
            log().info(f"[websocket_id:{websocket_session['id']}] Timeout detected. Closing "
                       f"WebSocket due to inactivity.")
            await close_websocket(websocket, websocket_session)
            return


async def close_websocket(websocket: WebSocket, websocket_session: dict):
    try:
        log().debug(f"[websocket_id:{websocket_session['id']}] closing websocket. Transmitted "
                    f"{websocket_session['tokens_transmitted']} tokens total.")
        websocket_session['closed'] = True
        await websocket.close()
    except RuntimeError:
        log().debug(f"[websocket_id:{websocket_session['id']}] WebSocket already closed")
