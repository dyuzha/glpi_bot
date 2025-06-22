# services/glpiservice.py

from dataclasses import dataclass

from glpi_bot.glpi.models import GLPIInterface, GLPIUser
from glpi_bot.glpi.session import GLPISessionManager
from glpi_bot.services.async_cache import AsyncBaseCache


REQUEST_TYPE_TELEGRAM = 14


@dataclass
class TicketData:
    login: str
    name: str
    content: str
    type: int
    itilcategories_id: int


class OrganisationCache(AsyncBaseCache):
    def __init__(self, session_manager):
        super().__init__(ttl_seconds=None)
        self.session_manager = session_manager

    async def load(self, session=None):
        if session is None:
            with self.session_manager.get_session() as session:
                return await GLPIInterface(session).get_all_entities()
        else:
            return await GLPIInterface(session).get_all_entities()


class GLPITicketManager:
    def __init__(self,
                 session_manager: GLPISessionManager,
                 org_cache: OrganisationCache
                 ):
        self.session_manager = session_manager
        self.org_cache = org_cache

    async def send_ticket(self, ticket_data: TicketData) -> dict:
        async with self.session_manager.get_session() as session:
            glpi = GLPIInterface(session)

            user = await glpi.get_user(ticket_data.login)
            if not isinstance(user, GLPIUser):
                raise ValueError(f"Пользователь '{ticket_data.login}' не найден")

            org_data = await self.org_cache.get(session=session)

            if user.organisation not in org_data:
                raise ValueError(f"Организация '{user.organisation}' не найдена")

            result = await glpi.create_ticket(
                name=ticket_data.name,
                content=ticket_data.content,
                type=ticket_data.type,
                requesttypes_id=REQUEST_TYPE_TELEGRAM,
                itilcategories_id=ticket_data.itilcategories_id,
                _users_id_requester=user.id,
                entities_id=org_data[user.organisation],
            )
            return result or {}
