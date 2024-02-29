from contextvars import ContextVar
import peewee
import sys

from config.settings import get_settings


db_state_default = {'closed': None, 'conn': None, 'ctx': None, 'transactions': None}
db_state = ContextVar('db_state', default=db_state_default.copy())


class PeeweeConnectionState(peewee._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__('_state', db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


def create_postgres_database_connection():
    return peewee.PostgresqlDatabase(
        get_settings().POSTGRES_DB,
        user=get_settings().POSTGRES_USER,
        password=get_settings().POSTGRES_PASSWORD,
        host=get_settings().POSTGRES_SERVER,
        port=get_settings().POSTGRES_PORT,
    )


def create_test_database_connection():
    return peewee.SqliteDatabase('/tmp/kth-assistant.test.db')


if 'pytest' in sys.modules:
    db = create_test_database_connection()
else:
    db = create_postgres_database_connection()


db._state = PeeweeConnectionState()
