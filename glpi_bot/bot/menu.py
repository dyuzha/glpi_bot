from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/delete_me", description="Удалить меня из базы данных"),
    ]
    await bot.set_my_commands(commands)


async def remove_bot_commands(bot: Bot):
    await bot.delete_my_commands()
