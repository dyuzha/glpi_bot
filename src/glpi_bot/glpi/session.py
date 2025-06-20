# glpi/session.py

import asyncio
import logging
from typing import Optional
from aiohttp import ClientError, ClientTimeout, ClientSession
from datetime import datetime, timedelta
from contextlib import asynccontextmanager


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
        self._client = ClientSession()
        self._lock = asyncio.Lock()


    @asynccontextmanager
    async def get_session(self):
        """Контекстный менеджер для работы с сессией GLPI"""
        try:
            async with self._lock:
                if self._is_token_expired():
                    await self._open_session()
            yield self
        except Exception as e:
            logger.error(f"Ошибка во время работы сессии: {e}")
            raise


    @property
    def client_session(self) -> ClientSession:
        return self._client


    async def shutdown(self):
        """Явно закрывает сессию HTTP client'a"""
        await self._close_session()
        await self._client.close()


    async def _open_session(self):
        """Установка соединения"""
        try:
            async with self._client.post(
                    f"{self.url}/initSession",
                    headers={
                             'Content-Type': 'application/json',
                             'App-Token': self._app_token,
                             },
                    json=self._auth_data,
                    timeout=ClientTimeout(total=10)
                    ) as response:

                response.raise_for_status()
                data = await response.json()

                self._session_token = data.get('session_token')
                self._token_expires = datetime.now() + timedelta(minutes=5)
                logger.info(f"Сессия успешно открыта")


        except ClientError as e:
            self._session_token = None
            self._token_expires = None
            logger.error(f"Ошибка подключения к GLPI: {e}", exc_info=True)
            raise ConnectionError(f"Ошибка подключения к GLPI: {e}") from e


    async def _close_session(self):
        """Закрытие соединения"""
        if not self._session_token:
            return

        try:
            async with self._client.get(
                f"{self.url}/killSession",
                headers={
                    'Session-Token': self._session_token,
                    'App-Token': self._app_token
                },
                timeout=ClientTimeout(total=5)
            ):
                logger.info("Сессия успешно закрыта")

        except ClientError as e:
            logger.warning(f"Не удалось закрыть сессию: {e}")
        finally:
            self._session_token = None
            self._token_expires = None


    def _is_token_expired(self) -> bool:
        """Проверяет истек ли срок действия токена сессии.

        Returns:
            bool: True если токен истек или не установлен, False если активен
        """
        if not self._token_expires:
            return True
        return datetime.now() >= self._token_expires


    async def _force_kill_previous_session(self):
        """Принудитльное завершение предыдущей сесии"""
        try:
            if self._session_token:
                async with self._client.get(
                    f"{self.url}/killSession",
                    headers={
                        'Session-Token': self._session_token,
                        'App-Token': self._app_token
                    },
                    timeout=ClientTimeout(total=3)
                    ) as response:
                        await response.text()
        except Exception:
            logger.debug("Не удалось завершить предыдущую сессию", exc_info=True)
