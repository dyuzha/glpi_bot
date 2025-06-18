# services/glpiservice.py
from dataclasses import dataclass

from glpi_bot.glpi.models import GLPIInterface
from glpi_bot.glpi.session import GLPISessionManager
from glpi_bot.services.cache import BaseCache


REQUEST_TYPE_TELEGRAM = 14


@dataclass
class TicketData:
    login: str
    name: str
    content: str
    type: int
    itilcategories_id: int


class OrganisationCache(BaseCache):
    def __init__(self, session_manager):
        super().__init__(ttl_seconds=None)
        self.session_manager = session_manager

    # def load(self) -> dict:
    #     with self.session_manager.get_session() as session:
    #         return GLPIInterface(session).get_all_entities()

    def load(self, session=None) -> dict:
        if session is None:
            with self.session_manager.get_session() as session:
                return GLPIInterface(session).get_all_entities()
        else:
            return GLPIInterface(session).get_all_entities()


class GLPITicketManager:
    def __init__(self, session_manager: GLPISessionManager, org_cache: OrganisationCache):
        self.session_manager = session_manager
        self.org_cache = org_cache

    def send_ticket(self, ticket_data: TicketData) -> dict:
        with self.session_manager.get_session() as session:
            glpi = GLPIInterface(session)

            user = glpi.get_user(ticket_data.login)
            if user is None:
                raise ValueError(f"Пользователь '{ticket_data.login}' не найден")

            org_data = self.org_cache.get(session=session)
            if user.organisation not in org_data:
                raise ValueError(f"Организация '{user.organisation}' не найдена")

            return glpi.create_ticket(
                name=ticket_data.name,
                content=ticket_data.content,
                type=ticket_data.type,
                requesttypes_id=REQUEST_TYPE_TELEGRAM,
                itilcategories_id=ticket_data.itilcategories_id,
                _users_id_requester=user.id,
                entities_id=org_data[user.organisation],
            )
