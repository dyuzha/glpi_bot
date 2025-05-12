import logging
import requests
from .exceptions import LDAPError, LDAPUserNotFound


logger = logging.getLogger(__name__)


URL = "http://localhost:82/get_user/mail"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 10  # Таймаут соединения в секундах


def get_user_mail(login):
    """
    Получает email пользователя из AD

    Args:
        login: Логин пользователя (sAMAccountName)

    Returns:
        Email пользователя

    Raises:
        LDAPError: Если произошла ошибка при запросе
        LDAPUserNotFound: Если пользователь не найден
        ValueError: Если неверный формат ответа
    """

    data = {
        "sAMAccountName": login,
        "ou": "OU=krd",
        "domain": "art-t.ru"
    }

    try:
        response = requests.post(
                URL,
                headers=HEADERS,
                json=data,
                timeout=TIMEOUT
                )

        # Обраьбатываем HTTP-ошибки
        if response.status_code == 404:
            raise LDAPUserNotFound()

        # Генерируем исключения для HTTP-ошибок
        # response.raise_for_status()


        parsed_data = response.json()

        # # Проверяем структуру ответа
        # if not isinstance(parsed_data, dict) \
        #     or parsed_data.get("status") != "success":
        #     raise LDAPError()

        if not parsed_data.get("data", {}).get("mail"):
            raise ValueError("Email не найден в ответе")

        return parsed_data["data"]["mail"]


    except requests.exceptions.RequestException as e:
        raise LDAPError() from e

    except (ValueError, KeyError) as e:
        raise ValueError(f"Ошибка при обработке ответа сервера: {str(e)}") from e
