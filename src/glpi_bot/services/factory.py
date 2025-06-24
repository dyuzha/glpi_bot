# services/factory.py

from glpi_bot.config_handlers import MAIL_DATA, GLPI_DATA
from glpi_bot.database import Database, DBSessionManager
from glpi_bot.glpi import GLPISessionManager

from .db_service import DBService
from .mail_service import EmailConfirmation
from .glpi_service import GLPITicketManager, OrganisationCache
from .ad import get_user_mail


async def create_db_service():
    db = Database('sqlite+aiosqlite:////data/users.db')
    await db.create_tables()
    db_session_manager = DBSessionManager(db)
    db_service = DBService(db_session_manager)

    return db_service


def create_mail_service():
    mail_confirmation = EmailConfirmation(**MAIL_DATA)

    return mail_confirmation


def create_glpi_service():
    glpi_session_manager = GLPISessionManager(**GLPI_DATA)
    org_cache = OrganisationCache(glpi_session_manager)
    glpi_service = GLPITicketManager(glpi_session_manager, org_cache)

    return glpi_service


async def create_services():
    db_service = await create_db_service()
    mail_confirmation = create_mail_service()
    glpi_service = create_glpi_service()

    return {
        "db_service": db_service,
        "mail_confirmation": mail_confirmation,
        "glpi_service": glpi_service,
        "ldap_func": get_user_mail,
    }
