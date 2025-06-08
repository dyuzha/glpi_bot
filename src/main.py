# main.py

from glpi_bot.config_handlers import setup_logging
from glpi_bot.services.factory import create_services
from glpi_bot.bot import create_bot

logger = setup_logging()



async def main():
    logger.info("Starting bot")
    services = create_services()

    await on_startup()

    await dp.start_polling(bot, db, mail, glpi)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
