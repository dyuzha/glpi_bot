# glpi/api.py

import logging
import requests
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GLPIConnection:
    """Контекстный менеджер для работы с GLPI API"""
    def __init__(self, url: str, app_token: str, username: str, password: str):
        """
        Инициализация подключения
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

    def __enter__(self):
        """Открытие сессии при входе в контекст"""
        self._force_kill_previous_session()
        self._open_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из контекста"""
        self._close_session()
        if exc_type is not None:
            logger.warning(f"Произошла ошибка: {exc_val}")
            raise exc_type
        return True

    def _force_kill_previous_session(self):
        try:
            if hasattr(self, 'session_token'):
                requests.get(
                    f"{self.url}/killSession",
                    headers={
                        'Session-Token': self.session_token,
                        'App-Token': self.app_token
                    },
                    timeout=3
                )
        except:
            pass

    def _open_session(self):
        """Установка соединения с GLPI API"""
        try:
            response = requests.post(
                f"{self.url}/initSession",
                headers={
                    'Content-Type': 'application/json',
                    'App-Token': self.app_token
                },
                json=self.auth_data,
                timeout=10
            )
            response.raise_for_status()
            # logging.info(f"Request: {response.request.headers}")

            self.session_token = response.json().get('session_token')
            logger.info(f"Given token : {self.session_token}")
            print(f"Given token : {self.session_token}")
            self.token_expires = datetime.now() + timedelta(minutes=5)  # Токен будет жить 5 минут
            # self.token_expires = datetime.now() + timedelta(hours=1)  # Токен будет жить 15 минут
            print("Сессия успешно открыта")

        except requests.exceptions.RequestException as e:

            raise ConnectionError(f"Ошибка подключения к GLPI: {str(e)}") from e

    def _close_session(self):
        """Закрытие сессии GLPI"""
        if not self.session_token:
            return

        try:
            requests.get(
                f"{self.url}/killSession",
                headers={
                    'Session-Token': self.session_token,
                    'App-Token': self.app_token
                },
                timeout=5
            )
            print("Сессия успешно закрыта")

        except requests.exceptions.RequestException as e:
            print(f"Предупреждение: не удалось закрыть сессию: {str(e)}")
        finally:
            self.session_token = None
            self.token_expires = None

    def _make_request(self, method: str, endpoint: str, json_data: dict = None):
        """
        Выполнение запроса к API GLPI
        :param method: HTTP метод (GET, POST, PUT, DELETE)
        :param endpoint: Конечная точка API (например, 'Ticket')
        :param json_data: Данные для отправки (уже должны быть в формате {'input': {...}})
        :return: Ответ API
        """
        if not self.session_token:
            raise ConnectionError("Сессия не открыта")

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
