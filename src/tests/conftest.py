# conftest.py

import logging
import pytest
from datetime import datetime

from glpi_bot.glpi.session import GLPISessionManager
from glpi_bot.services.mail_service import EmailConfirmation
from tests.test_env import GLPIEnv, MailEnv


def pytest_configure():
    logging.basicConfig(
        level=logging.DEBUG,  # или INFO
        format="%(levelname)s:%(name)s:%(message)s"
    )


@pytest.fixture
def email_confirmation():
    mail_confirmation = EmailConfirmation(
        smtp_server=MailEnv.SMTP_SERVER,
        smtp_port=MailEnv.SMTP_PORT,
        smtp_username=MailEnv.SMTP_USERNAME,
        smtp_password=MailEnv.SMTP_PASSWORD,
        use_tls=MailEnv.USE_TLS
    )
    return mail_confirmation


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

