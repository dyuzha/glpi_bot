from config_handlers import setup_logging
from bot import bot, dp


# Инициализация логирования ДО всего остального
logger = setup_logging()

async def main():
    logger.info("Starting bot")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
