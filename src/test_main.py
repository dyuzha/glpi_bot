# test_main.py

from tests.mocks import create_mock_services
from glpi_bot.bot import create_bot
from tests.test_env import TELEGRAM_TOKEN

import logging


def setup_logging(level: int = logging.DEBUG) -> logging.Logger:
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()  # убираем дубли
    root_logger.addHandler(handler)

    return logging.getLogger("glpi_bot")


logger = setup_logging()


async def main():
    logger.info("Starting bot")

    services = create_mock_services()

    bot, dp, on_startup = create_bot(services, TELEGRAM_TOKEN)

    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
