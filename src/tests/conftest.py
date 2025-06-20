# conftest.py

import logging
import pytest
from datetime import datetime

from glpi_bot.glpi.session import GLPISessionManager
from tests.test_env import GLPIEnv


def pytest_configure():
    logging.basicConfig(
        level=logging.DEBUG,  # или INFO
        format="%(levelname)s:%(name)s:%(message)s"
    )


@pytest.fixture
async def session_manager():
    manager = GLPISessionManager(
        url=GLPIEnv.URL,
        app_token=GLPIEnv.APP_TOKEN,
        username=GLPIEnv.USERNAME,
        password=GLPIEnv.PASSWORD,
    )
    yield manager
    await manager.shutdown()


@pytest.fixture
def frozen_now():
    return datetime(2023, 1, 1, 12, 0, 0)

