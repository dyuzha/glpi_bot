# handlers/__init__.py

from typing import Callable
from aiogram import Dispatcher

# from .tickets import setup_tickets
from .authorization import setup_authorization
from .entrypoint import setup_entrypoint
from .admins import setup_admins_command


def register_handlers(
        dp: Dispatcher,
        db_service,
        mail_service,
        glpi_service,
        ldap_func: Callable[[str], str]
    ):

    # Инъекция зависимостей в модули
    authorization_router = setup_authorization(
            db_service,
            mail_service,
            ldap_func
    )
    entry_point_router = setup_entrypoint(db_service)
    admins_router = setup_admins_command(db_service)
    # tickets_router = setup_tickets(glpi_service)

    from .tickets import router as tickets_router
    # Вложенность роутеров
    dp.include_routers(
            tickets_router,
            entry_point_router,
            authorization_router,
            admins_router
        )
