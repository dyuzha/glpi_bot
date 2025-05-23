# /database/base.py - Инициализация бд

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class Database:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self, Base):
        Base.metadata.create_all(bind=self.engine)
