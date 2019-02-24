from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()


class Database(object):

    def __init__(self, db_url, pool_size=5):
        self.db_url = db_url
        self.engine = None
        self.pool_size = pool_size

    def connect(self):
        # https://docs.sqlalchemy.org/en/latest/core/pooling.html#disconnect-handling-pessimistic
        driver = make_url(self.db_url).get_driver_name()
        kwargs = {}
        if driver != 'pysqlite':  # All drivers but sqlite have pool_size
            kwargs['pool_size'] = self.pool_size
        self.engine = create_engine(self.db_url, pool_pre_ping=True, **kwargs)

    @contextmanager
    def session(self):
        scoped = scoped_session(sessionmaker())
        scoped.configure(bind=self.engine)
        session = scoped()

        try:
            yield session
        finally:
            scoped.remove()
