# main.py

from glpi_bot.config_handlers import setup_logging
from glpi_bot.services.factory import create_services
from glpi_bot.bot import create_bot


logger = setup_logging()


async def main():
    logger.info("Starting bot")

    services = create_services()

    bot, dp, on_startup = create_bot(services)

    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
