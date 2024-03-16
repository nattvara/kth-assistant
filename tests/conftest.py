from unittest.mock import AsyncMock
import sys
import os

from transformers import AutoModelForCausalLM, AutoTokenizer
from websockets import WebSocketClientProtocol
from fastapi.testclient import TestClient
from numpy.random import rand, randint
import pytest

from services.llm.supported_models import LLMModel

# this will fix issue where the python path won't contain the packages
# in the main project when running inside pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.models import all_models, Session, Course, Chat, Message  # noqa
from config.settings import Settings  # noqa
from db.connection import db  # noqa
import http_api  # noqa


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
    client = TestClient(http_api.get_app())
    return client


@pytest.fixture
def mock_load_hf_model(mocker):
    mock_model = mocker.create_autospec(AutoModelForCausalLM)
    mock_tokenizer = mocker.create_autospec(AutoTokenizer)
    load_hf_model = mocker.patch(
        'llms.generate.load_hf_model',
        return_value=(mock_model, mock_tokenizer)
    )
    return load_hf_model


@pytest.fixture
def create_mock_generate_text_streaming(mocker):
    def create_mock(mock_tokens):
        async def mock_generate_text_func(model, tokenizer, device, params, prompt):
            for token in mock_tokens:
                yield token

        mock_generate_text_streaming = mocker.patch(
            'llms.generate.generate_text_streaming',
            side_effect=mock_generate_text_func
        )
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


@pytest.fixture
def llm_model_name():
    return LLMModel.MISTRAL_7B_INSTRUCT


@pytest.fixture
def llm_prompt():
    return "tell me a fact"


@pytest.fixture
def authenticated_session():
    class AuthenticatedSession:
        def __init__(self, session: Session):
            self.session = session
            self.headers = {'X-Session-ID': valid_session.public_id}

    valid_session = Session()
    valid_session.save()

    return AuthenticatedSession(valid_session)


@pytest.fixture
def valid_course():
    course = Course(canvas_id="41428")
    course.save()
    return course


@pytest.fixture
def new_chat(authenticated_session, valid_course):
    class NewChat:
        def __init__(self, chat: Chat, course: Course):
            self.course = course
            self.chat = chat

        def add_some_messages(self):
            for _ in range(randint(5, 10)):
                if rand() > 0.5:
                    sender = Message.Sender.STUDENT
                else:
                    sender = Message.Sender.ASSISTANT

                msg = Message(sender=sender, content=f'Hello from {sender}!', chat=self.chat)
                msg.save()

    c = Chat(course=valid_course, session=authenticated_session.session)
    c.save()

    return NewChat(c, valid_course)
