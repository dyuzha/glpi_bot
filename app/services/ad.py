import logging
import requests
from .exceptions import LDAPError, LDAPUserNotFound


logger = logging.getLogger(__name__)


# URL = "http://localhost:82/get_user/mail"
# URL = "http://ad_api:8000/get_user/mail"  # Используем внутреннее имя контейнера
URL = "http://aac:8000/get_user/mail"  # Используем внутреннее имя контейнера
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
        logger.debug(f"Отправка запроса: URL={URL}, данные={data}")

        # Отправляем POST запрос
        response = requests.post(
                URL,
                headers=HEADERS,
                json=data,
                timeout=TIMEOUT
                )

        logger.debug(f"Raw response: status: {response.status_code}, text: {response.text}")

        # Обраьбатываем HTTP-ошибки
        if response.status_code == 404:

            raise LDAPUserNotFound(f"Пользователь {login} не найден")

        # Генерируем исключения для HTTP-ошибок
        response.raise_for_status()


        # Парсим JSON
        try:
            parsed_data = response.json()
            logger.debug(f"Полученные данные: {parsed_data}")
        except ValueError as e:
            raise ValueError("Невалидный JSON в ответе") from e

        # Проверяем статус успешности (если такой есть в API)
        if parsed_data.get("status") != "success":
            raise LDAPError(f"Запрос завершился с ошибкой: \
                    {parsed_data.get('message', 'Unknown error')}")

        if not parsed_data.get("data", {}).get("mail"):
            raise ValueError("Email не найден в ответе")

        return parsed_data["data"]["mail"]


    except requests.exceptions.Timeout:
        raise LDAPError("Таймаут при подключении к серверу") from None

    # except requests.exceptions.RequestException as e:
    #     raise LDAPError() from e

    except (ValueError, KeyError) as e:
        raise ValueError(f"Ошибка при обработке ответа сервера: {str(e)}") from e
