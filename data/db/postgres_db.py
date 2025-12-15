from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config.config import DB_USER, DB_PASSWORD, DB_PORT, DB_NAME


class PostgresDb:
    _instance = None

    #db config
    def __init__(self):
        self.Base = declarative_base()
        self._database_url = (
            f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@localhost:{DB_PORT}/{DB_NAME}"
        )
        self._engine = create_engine(self._database_url, echo=True, future=True)
        self._sessionmaker = sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        PostgresDb._instance = self

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = PostgresDb()
        return cls._instance

    def init(self):
        with self._engine.begin() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
        self.Base.metadata.create_all(self._engine)
        print("DB was initialized successfully")

    def session(self):
        return self._sessionmaker()


#global instance
db = PostgresDb.instance()
