import pytest
from glpi_bot.services.mail_service import EmailConfirmation
from tests.test_env import MailEnv
from tests.conftest import email_confirmation


async def test_email_confirmation_initialization(email_confirmation):
    assert email_confirmation.smtp_password == MailEnv.SMTP_PASSWORD
    assert email_confirmation.smtp_port == MailEnv.SMTP_PORT
    assert email_confirmation.smtp_username == MailEnv.SMTP_USERNAME
    assert email_confirmation.smtp_server == MailEnv.SMTP_SERVER
    assert email_confirmation.use_tls == MailEnv.USE_TLS


async def test_send_email(email_confirmation):
    code = await email_confirmation.send_confirmation_email(
            "dyuzhev_mn@it4prof.ru"
            )

    assert code is not None
