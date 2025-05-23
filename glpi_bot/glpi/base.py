# glpi/base.py

import logging
import requests
from typing import Optional
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class GLPIBase:
    def __init__(self, url: str, app_token: str, username: str, password: str):
        """
        :param glpi_url: URL GLPI (например, 'https://glpi.example.com/apirest.php')
        :param app_token: App-Token из настроек GLPI
        :param username: Логин пользователя API
        :param password: Пароль пользователя
        """
        self.url = url.rstrip('/')
        self.app_token = app_token
        self.auth_data = {
            'login': username,
            'password': password,
            'app_token': app_token
        }
        self.session_token: Optional[str] = None
        self.token_expires: Optional[datetime] = None

    def make_request(self, method: str, endpoint: str, json_data: Optional[dict]):
        """
        Выполнение запроса к API GLPI
        :param method: HTTP метод (GET, POST, PUT, DELETE)
        :param endpoint: Конечная точка API (например, 'Ticket')
        :param json_data: Данные для отправки
        :return: Ответ API
        """

        url = f"{self.url}/{endpoint}"
        headers = {
            'Session-Token': self.session_token,
            'App-Token': self.app_token,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request(
                method.upper(),
                url,
                headers=headers,
                json=json_data
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка API запроса: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError() from e
