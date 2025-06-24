from aiogram import Bot
from aiogram.types import BotCommand


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        # BotCommand(command="/delete_me", description="Отменить регистрацию"),
    ]
    await bot.set_my_commands(commands)


async def remove_bot_commands(bot: Bot):
    await bot.delete_my_commands()
