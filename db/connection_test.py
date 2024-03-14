"""
This module contains a thread-safe version of SqliteDatabase using thread-local storage. This
database class when running the testsuite.
"""

import threading

from peewee import SqliteDatabase


class ThreadLocalSqliteDatabase(SqliteDatabase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._locals = threading.local()

    def _connect(self, *args, **kwargs):
        if not hasattr(self._locals, 'conn'):
            self._locals.conn = super()._connect(*args, **kwargs)
        return self._locals.conn

    def connect(self, *args, **kwargs):
        return self._connect(*args, **kwargs)

    def close(self):
        if hasattr(self._locals, 'conn'):
            self._locals.conn.close()
            del self._locals.conn

    def commit(self):
        if hasattr(self._locals, 'conn'):
            return self._locals.conn.commit()
        else:
            raise peewee.InterfaceError('Database connection not available to commit.')

    def rollback(self):
        if hasattr(self._locals, 'conn'):
            return self._locals.conn.rollback()
        else:
            raise peewee.InterfaceError('Database connection not available to rollback.')

    def cursor(self, *args, **kwargs):
        self.connect()  # Ensure connection for the current thread before getting cursor
        return self._locals.conn.cursor(*args, **kwargs)
