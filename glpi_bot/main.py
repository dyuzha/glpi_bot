from config_handlers import setup_logging
from bot import bot, dp, set_bot_commands

# Инициализация логирования ДО всего остального
logger = setup_logging()


async def on_startup():
    """Действия при запуске бота"""
    await set_bot_commands(bot)
    logger.info("Меню для бота загруженно")

async def main():
    logger.info("Starting bot")
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
