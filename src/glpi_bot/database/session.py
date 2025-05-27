# /database/session.py - Управление сессиями

from contextlib import contextmanager
from glpi_bot.database import Database

class DBSessionManager:
    def __init__(self, database: Database):
        self.db = database

    @contextmanager
    def get_session(self):
        session = self.db.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
