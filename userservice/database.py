from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class Database:
    Base = declarative_base()

    def __init__(self, settings):

        self._session = None
        self.session = settings

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, settings):
        global Base

        password = settings.db_password
        host = settings.db_host
        database = settings.db_database
        user = settings.db_user

        engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}/{database}')
        db_session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=engine))

        Database.Base.query = db_session.query_property()

        self._session = db_session
