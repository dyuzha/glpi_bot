# glpi/session.py

import logging
import requests
from typing import Optional
from datetime import datetime, timedelta
from glpi_bot.glpi.models import GLPIInterface
from contextlib import contextmanager


logger = logging.getLogger(__name__)


class GLPISessionManager:
    """Контекстный менеджер для работы с GLPI API"""

    def __init__(self, glpi: GLPIInterface):
        self.glpi = glpi
        self.session_token: Optional[str]
        self.token_expires: Optional[datetime]


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
            if self.session_token:
                requests.get(
                    f"{self.glpi.url}/killSession",
                    headers={
                        'Session-Token': self.session_token,
                        'App-Token': self.glpi.app_token
                    },
                    timeout=3
                )
        except Exception:
            logger.debug("Не удалось завершить предыдущую сессию", exc_info=True)

    def _open_session(self):
        """Установка соединения с GLPI API"""
        try:
            response = requests.post(
                f"{self.glpi.url}/initSession",
                headers={
                    'Content-Type': 'application/json',
                    'App-Token': self.glpi.app_token
                },
                json=self.glpi.auth_data,
                timeout=10
            )
            response.raise_for_status()

            self.session_token = response.json().get('session_token')
            logger.info(f"Получен токен: {self.session_token}")
            print(f"Получен токен: {self.session_token}")
            # Установка времени жизни токена
            self.token_expires = datetime.now() + timedelta(minutes=5)
            logger.info(f"Сессия успешно открыта")
            print("Сессия успешно открыта")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка подключения к GLPI: {e}", exc_info=True)
            raise ConnectionError(f"Ошибка подключения к GLPI: {e}") from e

    def _close_session(self):
        """Закрытие сессии GLPI"""
        if not self.session_token:
            return

        try:
            requests.get(
                f"{self.glpi.url}/killSession",
                headers={
                    'Session-Token': self.session_token,
                    'App-Token': self.glpi.app_token
                },
                timeout=5
            )
            logger.info("Сессия успешно закрыта")

        except requests.exceptions.RequestException as e:
            logger.warning(f"Не удалось закрыть сессию: {e}")
        finally:
            self.session_token = None
            self.token_expires = None
