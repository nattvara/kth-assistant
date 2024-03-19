from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from config.logger import log
import config.settings as settings
from http_api.routers import (
    websocket,
    sessions,
    index,
    chat,
)


def get_app():
    app = FastAPI(title=settings.get_settings().NAME, openapi_url=None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip('/') for origin in settings.get_settings().BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(index.router)
    app.include_router(websocket.router)
    app.include_router(sessions.router)
    app.include_router(chat.router)

    return app


def main():
    log().info('http api is starting')

    app = get_app()

    return app
