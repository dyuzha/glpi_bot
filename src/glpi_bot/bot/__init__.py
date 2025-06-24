# bot/__init__.py

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from glpi_bot.bot.menu import set_bot_commands, remove_bot_commands
from glpi_bot.bot.handlers import register_handlers


def create_bot(services: dict, telegram_token):
    glpi_service = services["glpi_service"]
    db_service = services["db_service"]
    mail_service = services["mail_confirmation"]
    ldap_func = services["ldap_func"]

    bot = Bot(
            token=telegram_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    register_handlers(dp, db_service, mail_service, glpi_service, ldap_func)

    async def on_startup():
        """Действия при запуске бота"""
        await remove_bot_commands(bot)
        await set_bot_commands(bot)

    return bot, dp, on_startup
