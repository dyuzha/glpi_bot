import logging
from aiogram import types
from aiogram.filters import Command
from bot.keyboards import main_kb
from bot import dp

logger = logging.getLogger(__name__)  # Используем __name__ для автоматического определения имени модуля

# Обработчики команд
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я ПРОФИТ-бот для работы с GLPI.\n"
        "С моей помощью вы можете создать заявку.",
        reply_markup=main_kb()
    )
