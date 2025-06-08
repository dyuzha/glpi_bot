# handlers/__init__.py

from aiogram import Dispatcher

from .tickets import router as tickets_router, setup_tickets
from .authorization import router as authorization_router, setup_authorization
from .deffault import router as deffault_router, setup_deffault
from .admins import router as admins_router

def register_handlers(
        dp: Dispatcher,
        db_service,
        mail_service,
        glpi_service,
    ):

    # Инъекция зависимостей в модули
    setup_authorization(db_service, mail_service)
    setup_deffault(db_service)
    setup_tickets(glpi_service)

    # Вложенность роутеров
    dp.include_routers(
            tickets_router,
            deffault_router,
            authorization_router,
            admins_router
        )
