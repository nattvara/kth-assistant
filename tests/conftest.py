from unittest.mock import AsyncMock
import sys
import os

from transformers import AutoModelForCausalLM, AutoTokenizer
from websockets import WebSocketClientProtocol
from fastapi.testclient import TestClient
import pytest

# this will fix issue where the python path won't contain the packages
# in the main project when running inside pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import Settings
from db.models import all_models
from db.connection import db
import api


@pytest.fixture(autouse=True)
def tables_setup_teardown():
    db.create_tables(all_models)
    yield
    db.drop_tables(all_models)


@pytest.fixture(autouse=True)
def mock_settings(mocker):
    mock_settings = Settings(
        NAME="testsuite",
        BACKEND_CORS_ORIGINS=["http://localhost:1337"],
        HOST="localhost",
        PORT="8080",
        POSTGRES_SERVER="some_server",
        POSTGRES_PORT="some_port",
        POSTGRES_USER="some_user",
        POSTGRES_PASSWORD="some_password",
        POSTGRES_DB="some_db",
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
    )
    mocker.patch('config.settings.get_settings', return_value=mock_settings)


@pytest.fixture(autouse=True)
def suppress_logging(mocker):
    mocker.patch('logging.Logger.debug')
    mocker.patch('logging.Logger.info')
    mocker.patch('logging.Logger.warning')
    mocker.patch('logging.Logger.error')
    mocker.patch('logging.Logger.critical')


@pytest.fixture
def api_client():
    client = TestClient(api.get_app())
    return client


@pytest.fixture
def mock_load_hf_model(mocker):
    mock_model = mocker.create_autospec(AutoModelForCausalLM)
    mock_tokenizer = mocker.create_autospec(AutoTokenizer)
    load_hf_model = mocker.patch(
        'text.generate.load_hf_model',
        return_value=(mock_model, mock_tokenizer)
    )
    return load_hf_model


@pytest.fixture
def create_mock_generate_text_streaming(mocker):
    def create_mock(mock_tokens):
        async def mock_generate_text_func(model, tokenizer, device, params, prompt):
            for token in mock_tokens:
                yield token

        mock_generate_text_streaming = mocker.patch('text.generate.generate_text_streaming', side_effect=mock_generate_text_func)
        return mock_generate_text_streaming

    return create_mock


@pytest.fixture
def create_websocket_mocks(mocker):
    def create_mocks():
        mock_ws = AsyncMock(spec=WebSocketClientProtocol)
        mock_ctx_manager = AsyncMock()
        mock_ctx_manager.__aenter__.return_value = mock_ws
        mock_ctx_manager.__aexit__.return_value = None
        mock_connect = mocker.patch('websockets.connect', return_value=mock_ctx_manager)
        return mock_ws, mock_connect

    return create_mocks
