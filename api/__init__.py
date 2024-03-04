from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from config.logger import log
import config.settings as settings
from api.routers import (
    index,
    websocket,
)


def get_app():
    app = FastAPI(title=settings.get_settings().NAME, openapi_url=None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.get_settings().BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(index.router)
    app.include_router(websocket.router)

    return app


def main():
    log().info('api is starting')

    app = get_app()

    return app
