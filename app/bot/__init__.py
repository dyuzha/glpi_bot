# bot/__init__.py
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config_handlers import TELEGRAM_TOKEN
from .middlewares import AuthMiddleware


# Используем __name__ для автоматического определения имени модуля
logger = logging.getLogger(__name__)


bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))
dp = Dispatcher()

from .handlers import *

# Регистрируем middleware
# dp.update.middleware(AuthMiddleware())

