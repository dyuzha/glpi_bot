# services/glpi_service.py

import logging
import requests
from typing import Optional
from datetime import datetime, timedelta
from glpi import GLPIInterface, GLPIUser, GLPISessionManager


logger = logging.getLogger(__name__)


class GLPIService(GLPIInterface):
    """Класс для составления заявок"""
    # Пробросить id источника запросов в конфиг

    def __init__(self, session_manager: GLPISessionManager):
        self.session_manager = session_manager

    def create_ticket(self, **data):
        # Получаем пользователя glpi
        with self.session_manager.get_session() as session:
            user = self.get_user(data["login"])
        if user is None:
            raise ValueError

        # Получаем id автора заявки
        user_id = user.get_id()

        # Выставляем его id в инициаторы заявки
        data["_users_id_requester"] = user_id

        # Делаем источник заявки - телеграмм
        data["requesttypes_id"] = 14

        # Убираем login из входных данных
        del data["login"]

        # Создаем тикет с обновленными данными
        return super().create_ticket(**data)
