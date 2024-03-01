import sys
import os

import pytest
from fastapi.testclient import TestClient

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
        POSTGRES_SERVER="some_server",
        POSTGRES_PORT="some_port",
        POSTGRES_USER="some_user",
        POSTGRES_PASSWORD="some_password",
        POSTGRES_DB="some_db",
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
