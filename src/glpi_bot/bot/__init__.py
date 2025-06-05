# bot/__init__.py

import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from glpi_bot.config_handlers import TELEGRAM_TOKEN
from .models import AuthState
from aiogram.fsm.storage.memory import MemoryStorage
from glpi_bot.bot.handlers import tickets_router


logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(tickets_router)

# Регистрируем обработчики
from .handlers import *

# Регистрируем меню бота
from .menu import set_bot_commands


