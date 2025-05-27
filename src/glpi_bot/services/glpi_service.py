# services/glpi_service.py

import logging
from glpi_bot.glpi import GLPISessionManager, GLPIInterface
import logging
from typing import Optional


logger = logging.getLogger(__name__)


REQUEST_TYPE_TELEGRAM = 14


class GLPIService:
    """Класс для взаимодействия с GLPI"""
    def __init__(self, session_manager: GLPISessionManager):
        self.session_manager = session_manager
        self._organisation_data: Optional[dict] = None
        self._load_organisation_data()

    def get_glpi_interface(self, session) -> GLPIInterface:
        return GLPIInterface(session)

    def _load_organisation_data(self):
        if self._organisation_data is not None:
            return

        with self.session_manager.get_session() as session:
            glpi_interface = self.get_glpi_interface(session)
            self._organisation_data = glpi_interface.get_all_entities()

        if self._organisation_data is None:
            raise Exception("Ошибка во время поиска организации")

    @property
    def organisation_data(self):
        if self._organisation_data is None:
            self._load_organisation_data()
        return self._organisation_data



class GLPITicketManager(GLPIService):
    """Класс для взаимодействия с заявками в GLPI"""
    def __init__(self, session_manager: GLPISessionManager):
        self._organisation_data: Optional[dict] = None  # Инициализация перед super()
        super().__init__(session_manager)

    def send_ticket(self) -> dict:
         with self.session_manager.get_session() as session
        # self.organisation = organisation
        self.login = login

    def _to_dict(self):
        if self.users_id_requester is None:
            raise ValueError("Параметр users_id_requester пуст или не определен")

        if self.entities_id is None:
            raise ValueError("Параметр entities_id пуст или не определен")

        return {
            "name": self.name,
            "content": self.content,
            "type": self.type,
            "requesttypes_id": REQUEST_TYPE_TELEGRAM,
            "itilcategories_id": self.itilcategories_id,
            "_users_id_requester": self.users_id_requester,
            "entities_id": self.entities_id,
        }

    def _set_users_id_requester_and_entities_id(self, glpi_interface: GLPIInterface):
        glpi_user = glpi_interface.get_user(self.login)
        if glpi_user is None:
            raise ValueError("Пользователь не найден")
        if self.organisation_data is None:
            raise ValueError ("Параметр _organisation_data не задан или не определен")
        self.users_id_requester = glpi_user.id
        self.entities_id = self.organisation_data[glpi_user.organisation]
