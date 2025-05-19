# bot/__init__.py

import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config_handlers import TELEGRAM_TOKEN
from .middlewares import AuthMiddleware
from .models import AuthState
from aiogram.fsm.storage.memory import MemoryStorage


logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрируем обработчики
from .handlers import *

# Регистрируем меню бота
from .menu import set_bot_commands

# Регистрируем middleware
# dp.update.middleware(AuthMiddleware())

