# main.py
import asyncio

from glpi_bot.config_handlers import setup_logging
from glpi_bot.services.factory import create_services
from glpi_bot.config_handlers import TELEGRAM_TOKEN
from glpi_bot.bot import create_bot


logger = setup_logging()


async def main():
    logger.info("Starting bot")

    services = await create_services()
    glpi_service = services["glpi_service"]

    bot, dp, on_startup = create_bot(services, TELEGRAM_TOKEN)

    try:
        await on_startup()
        await dp.start_polling(bot)
    finally:
        await glpi_service.shutdown_session()



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Выход по Ctrl+C")
