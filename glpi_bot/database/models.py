# database/models.py - Модели

from sqlalchemy import Column, Integer, String
from database import Base, Database
from contextlib import contextmanager
import logging


logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    login = Column(String(20), nullable=False)

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, login='{self.login}')>"
