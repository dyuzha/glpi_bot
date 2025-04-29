# bot/__init__.py
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config_handlers import TELEGRAM_TOKEN


# Используем __name__ для автоматического определения имени модуля
logger = logging.getLogger(__name__)


from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config_handlers import TELEGRAM_TOKEN


bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Импорт обработчиков после инициализации dp
from .handlers import register_ticket_handlers
register_ticket_handlers(dp)
