from config_handlers import setup_logging
from bot import bot, dp
from mail import mail_sender


# Инициализация логирования ДО всего остального
logger = setup_logging()

async def main():
    logger.info("Starting bot")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
