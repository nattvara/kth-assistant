from unittest.mock import AsyncMock, create_autospec, MagicMock
import sys
import os

from playwright.async_api import Browser, BrowserContext, Page
from transformers import AutoModelForCausalLM, AutoTokenizer
from websockets import WebSocketClientProtocol
from fastapi.testclient import TestClient
from numpy.random import rand, randint
from redis.asyncio import Redis
import pytest

# this will fix issue where the python path won't contain the packages
# in the main project when running inside pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.models import all_models, Session, Course, Chat, Message, ChatConfig, Snapshot, Url, Content, FaqSnapshot  # noqa
from services.download.download import DownloadService  # noqa
from services.index.supported_indices import IndexType  # noqa
from services.llm.supported_models import LLMModel  # noqa
from services.crawler.crawler import CrawlerService  # noqa
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
        COOKIE_IDENTIFIER="the-cookie",
        CANVAS_PROFILE_PAGE_VALIDATION_SEARCH_STRING="Test Testsson",
        POSTGRES_SERVER="some_server",
        POSTGRES_PORT="some_port",
        POSTGRES_USER="some_user",
        POSTGRES_PASSWORD="some_password",
        POSTGRES_DB="some_db",
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        OPENSEARCH_HOST="localhost",
        OPENSEARCH_PORT=9200,
        OPENSEARCH_USERNAME="admin",
        OPENSEARCH_PASSWORD="admin",
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
def create_mock_compute_embedding(mocker):
    def create_mock(vector):
        mock_compute_embeddings = mocker.patch(
            'llms.embeddings.compute_embedding',
            return_value=vector
        )
        return mock_compute_embeddings

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
    config = ChatConfig(llm_model_name=LLMModel.MISTRAL_7B_INSTRUCT, index_type=IndexType.NO_INDEX)
    config.save()

    course = Course(canvas_id="41428", snapshot_lifetime_in_mins=60)
    course.save()

    snapshot = FaqSnapshot(course=course)
    snapshot.save()

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

    config = ChatConfig(llm_model_name=LLMModel.MISTRAL_7B_INSTRUCT, index_type=IndexType.NO_INDEX)
    config.save()

    c = Chat(
        course=valid_course,
        session=authenticated_session.session,
        llm_model_name=config.llm_model_name,
        index_type=config.index_type
    )
    c.save()

    return NewChat(c, valid_course)


@pytest.fixture
def redis_connection(mocker) -> Redis:
    mock_redis = create_autospec(Redis, instance=True)
    return mocker.patch('cache.redis.get_redis_connection', return_value=mock_redis)


@pytest.fixture
def new_snapshot(valid_course: Course):
    class NewSnapshot:
        def __init__(self, course: Course, snapshot: Snapshot):
            self.course = course
            self.snapshot = snapshot

        def add_unvisited_url(self) -> Url:
            url = Url(snapshot=self.snapshot, href="https://example.com/1", distance=0)
            url.save()
            return url

        def add_visited_url(self) -> Url:
            url = Url(
                snapshot=self.snapshot,
                href="https://example.com/1",
                distance=0,
                state=Url.States.VISITED,
            )
            url.save()
            return url

        def add_url_with_content(self) -> Url:
            url = Url(
                snapshot=self.snapshot,
                href="https://example.com/1",
                distance=0,
                state=Url.States.DOWNLOADED,
            )

            content = Content(text="some content", name="file.pdf")
            content.save()
            url.content = content
            url.save()

            return url

    s = Snapshot(course=valid_course)
    s.save()

    return NewSnapshot(valid_course, s)


@pytest.fixture
async def get_crawler_service(redis_connection, playwright_session):
    playwright_session

    class CrawlerServiceFixture:

        def __init__(self, service: CrawlerService, playwright: object, redis_conn: Redis):
            self.service = service
            self.playwright = playwright
            self.redis_conn = redis_conn

    s = CrawlerService(
        redis_connection,
        playwright_session.browser,
        playwright_session.context,
        playwright_session.page
    )

    return CrawlerServiceFixture(s, playwright_session, redis_connection)


@pytest.fixture
async def get_download_service(playwright_session):
    class DownloadServiceFixture:

        def __init__(self, service: DownloadService, playwright: object):
            self.service = service
            self.playwright = playwright

    s = DownloadService(
        playwright_session.browser,
        playwright_session.context,
        playwright_session.page
    )

    return DownloadServiceFixture(s, playwright_session)


@pytest.fixture
def playwright_session(mocker):
    class PlaywrightSession:
        def __init__(self, browser: Browser, context: BrowserContext, page: Page):
            self.browser = browser
            self.context = context
            self.page = page

    mock_response = AsyncMock()
    mock_browser = mocker.MagicMock()
    mock_context = mocker.MagicMock()
    mock_page = mocker.MagicMock()

    mock_response.status = 200

    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)

    mock_page.goto = AsyncMock()
    mock_page.wait_for_load_state = AsyncMock()
    mock_page.goto = AsyncMock(return_value=mock_response)

    mock_chromium = MagicMock()
    mock_chromium.launch = AsyncMock(return_value=mock_browser)

    mock_playwright = MagicMock()
    mock_playwright.chromium = mock_chromium

    mocker.patch('playwright.async_api.async_playwright', return_value=AsyncMock(
        __aenter__=AsyncMock(return_value=mock_playwright),
        __aexit__=AsyncMock(),
    ))

    mocker.patch(
        'services.crawler.playwright.get_logged_in_browser_context_and_page',
        return_value=(mock_browser, mock_context, mock_page)
    )

    session = PlaywrightSession(mock_browser, mock_context, mock_page)

    return session
