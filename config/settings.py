from typing import List, Optional

from pydantic import HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    NAME: str = "kth-assistant"

    HOST: str
    PORT: int
    BACKEND_CORS_ORIGINS: List[HttpUrl] = []
    WEBSOCKET_TIMEOUT_DURATION: int = 30
    LLM_WORKER_SHUTDOWN_DELAY_SECONDS: int = 15
    COOKIE_IDENTIFIER: str

    QUEUE_WORKER_QUEUE_NAME: Optional[str] = None

    NUMBER_OF_CRAWLER_WORKERS: int = 3
    CRAWLER_MODE_IS_HEADLESS: bool = True
    CANVAS_PROFILE_PAGE_VALIDATION_SEARCH_STRING: str

    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: int

    OPENSEARCH_HOST: str
    OPENSEARCH_PORT: int
    OPENSEARCH_USERNAME: str
    OPENSEARCH_PASSWORD: str

    HUGGINGFACE_ACCESS_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


def get_settings() -> Settings:
    return Settings()
