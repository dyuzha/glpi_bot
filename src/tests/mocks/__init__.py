from types import SimpleNamespace

from glpi_bot.database.session import DBSessionManager


class MockDBService:
    def get_login(self, telegram_id: int) -> str | None:
        return "test_user"


class MockGLPIService:
    def send_ticket(self, ticket_data):
        # print(f"[MOCK] Создание тикета: {ticket_data}")
        return {"id":1234}  # поддельный ticket ID


class DBService:
    def __init__(self, *args, **kwargs):
        ...

    def check_user(self, telegram_id: int) -> bool:
        return True

    def get_login(self, telegram_id: int):
        return "test_login"

    def delete_user(self, telegram_id: int) -> bool:
        return True


class MockMailService:
    async def send_confirmation_email(self, email_to: str, length=4):
        return 1234


def get_user_mail(login):
    return "test_user@example.domain"


def create_mock_services() -> dict:
    return {
        "db_service": MockDBService(),
        "mail_confirmation": MockMailService(),
        "glpi_service": MockGLPIService(),
        "ldap_func": get_user_mail,
    }
