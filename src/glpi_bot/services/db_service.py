from glpi_bot.database import User, DBSessionManager
import logging


logger = logging.getLogger(__name__)


class DBService:
    def __init__(self, session_manager: DBSessionManager):
        self.session_manager = session_manager

    def save_user(self, telegram_id: int, login: str):
        with self.session_manager.get_session() as session:
            # Проверяем, есть ли уже такой пользователь
            user = session.query(User).filter_by(
                telegram_id= telegram_id).first()
            if user:
                # Обновляем данные существующего пользователя
                user.login = login
            else:
                # Создаем нового пользователя
                session.add(User(telegram_id=telegram_id, login=login))

    def check_user(self, telegram_id: int) -> bool:
        with self.session_manager.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            return user is not None

    def get_login(self, telegram_id: int):
        with self.session_manager.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            return user.login if user else None

    def delete_user(self, telegram_id: int) -> bool:
        with self.session_manager.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
