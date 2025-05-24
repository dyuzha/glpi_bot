# glpi/session.py

import logging
import requests
from typing import Optional
from datetime import datetime, timedelta
from contextlib import contextmanager


logger = logging.getLogger(__name__)


class GLPISessionManager:
    """Контекстный менеджер для работы с GLPI API"""

    def __init__(self, url: str, app_token: str, username: str, password: str):
        """
        :param glpi_url: URL GLPI (например, 'https://glpi.example.com/apirest.php')
        :param app_token: App-Token из настроек GLPI
        :param username: Логин пользователя API
        :param password: Пароль пользователя
        """
        self.url = url.rstrip('/')
        self._app_token = app_token
        self._auth_data = {
            'login': username,
            'password': password,
            'app_token': app_token
        }
        self._session_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None


    @contextmanager
    def get_session(self):
        """Контекстный менеджер для работы с сессией GLPI"""
        try:
            self._open_session()
            yield self
        except Exception as e:
            logger.error(f"Ошибка во время работы сессии: {e}")
            raise
        finally:
            self._close_session


    def _force_kill_previous_session(self):
        """Принудитльное завершение предыдущей сесии"""
        try:
            if self._session_token:
                requests.get(
                    f"{self.url}/killSession",
                    headers={
                        'Session-Token': self._session_token,
                        'App-Token': self._app_token
                    },
                    timeout=3
                )
        except Exception:
            logger.debug("Не удалось завершить предыдущую сессию", exc_info=True)

    def _open_session(self):
        """Установка соединения с GLPI API"""
        try:
            response = requests.post(
                f"{self.url}/initSession",
                headers={
                    'Content-Type': 'application/json',
                    'App-Token': self._app_token
                },
                json=self._auth_data,
                timeout=10
            )
            response.raise_for_status()

            self._session_token = response.json().get('session_token')
            logger.info(f"Получен токен: {self._session_token}")
            print(f"Получен токен: {self._session_token}")
            # Установка времени жизни токена
            self._token_expires = datetime.now() + timedelta(minutes=5)
            logger.info(f"Сессия успешно открыта")
            print("Сессия успешно открыта")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка подключения к GLPI: {e}", exc_info=True)
            raise ConnectionError(f"Ошибка подключения к GLPI: {e}") from e

    def _close_session(self):
        """Закрытие сессии GLPI"""
        if not self._session_token:
            return

        try:
            requests.get(
                f"{self.url}/killSession",
                headers={
                    'Session-Token': self._session_token,
                    'App-Token': self._app_token
                },
                timeout=5
            )
            logger.info("Сессия успешно закрыта")

        except requests.exceptions.RequestException as e:
            logger.warning(f"Не удалось закрыть сессию: {e}")
        finally:
            self._session_token = None
            self._token_expires = None
