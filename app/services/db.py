from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    login: Mapped[str] = mapped_column(String(20), nullable=False)

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, login='{self.login}')>"

engine = create_engine('sqlite:///users.db')

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class DBInterface:
    @classmethod
    def save_user(cls, telegram_id: int, login: str):
        session = Session()
        try:
            # Проверяем, есть ли уже такой пользователь
            existing_user = session.query(Users).filter_by(telegram_id=
                                                          telegram_id).first()
            if existing_user:
                # Обновляем данные существующего пользователя
                existing_user.login = login
            else:
                # Создаем нового пользователя
                new_user = Users(telegram_id=telegram_id, login=login)
                session.add(new_user)

            session.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения пользователя в БД: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    @classmethod
    def check_user(cls, telegram_id: int) -> bool:
        session = Session()
        user = session.query(Users).filter_by(telegram_id=telegram_id).first()
        session.close()
        return user is not None


    @classmethod
    def get_login(cls, telegram_id: int) -> str | None:
        with Session() as session:
            user = session.query(Users).filter_by(telegram_id=telegram_id).first()
            return user.login if user else None
