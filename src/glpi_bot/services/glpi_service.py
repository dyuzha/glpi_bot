# services/glpi_service.py

import logging
from glpi_bot.glpi import GLPISessionManager, GLPIInterface


logger = logging.getLogger(__name__)


class GLPIService:
    """Класс для составления заявок"""
    # Пробросить id источника запросов в конфиг

    REQUEST_TYPE_TELEGRAM = 14

    def __init__(self, session_manager: GLPISessionManager):
        self.session_manager = session_manager

    def _get_glpi_interface(self, session) -> GLPIInterface:
        return GLPIInterface(session)

    def create_ticket(self, **data):
        # Получаем пользователя glpi
        with self.session_manager.get_session() as session:
            glpi_interface = self._get_glpi_interface(session)

            # Получаем пользователя
            user = glpi_interface.get_user(data["login"])
            if user is None:
                raise ValueError

            # Выставляем его id в инициаторы заявки
            data.update({
                "_users_id_requester": user.get_id(),
                "requesttypes_id": self.REQUEST_TYPE_TELEGRAM
            })

            # Убираем login из входных данных
            del data["login"]

            # Создаем заявку
            glpi_interface.create_ticket(**data)
