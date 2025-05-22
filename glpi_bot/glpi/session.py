# glpi/session.py

import logging
import requests
from typing import Optional
from datetime import datetime, timedelta
from glpi import GLPIConnection


logger = logging.getLogger(__name__)


class GLPIContextManager:
    """Контекстный менеджер для работы с GLPI API"""
    def __init__(self, glpi_base: GLPIConnection):
        self.glpi_base = glpi_base

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
                    f"{self.glpi_base.url}/killSession",
                    headers={
                        'Session-Token': self.session_token,
                        'App-Token': self.glpi_base.app_token
                    },
                    timeout=3
                )
        except:
            pass

    def _open_session(self):
        """Установка соединения с GLPI API"""
        try:
            response = requests.post(
                f"{self.glpi_base.url}/initSession",
                headers={
                    'Content-Type': 'application/json',
                    'App-Token': self.glpi_base.app_token
                },
                json=self.glpi_base.auth_data,
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
                f"{self.glpi_base.url}/killSession",
                headers={
                    'Session-Token': self.session_token,
                    'App-Token': self.glpi_base.app_token
                },
                timeout=5
            )
            print("Сессия успешно закрыта")

        except requests.exceptions.RequestException as e:
            print(f"Предупреждение: не удалось закрыть сессию: {str(e)}")
        finally:
            self.session_token = None
            self.token_expires = None



