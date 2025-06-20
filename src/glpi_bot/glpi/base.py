# glpi/base.py

import logging
import aiohttp
from typing import Optional

from aiohttp.client import ContentTypeError
from glpi_bot.glpi.session import GLPISessionManager


logger = logging.getLogger(__name__)


class GLPIError(Exception):
    """Базовое исключение для ошибок GLPI"""
    pass


class GLPIRequestError(GLPIError):
    """Ошибка сетевого запроса"""
    pass


class GLPIUnauthorizedError(GLPIError):
    """Ошибка авторизации"""
    pass


class GLPIAPIError(Exception):
    """Ошибка API"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class GLPIBase:
    """
    Базовый класс для работы с GLPI API

    Args:
        session_manager (GLPISessionManager): Менеджер сессий для работы с GLPI
    """

    DEFAULT_TIMEOUT = 10
    BASE_HEADERS = {}
    # BASE_HEADERS = {
    #         'Content-Type': 'application/json',
    #         'Accert': 'application/json'
    #         }


    def __init__(self, session_manager: GLPISessionManager):
        self.session_manager = session_manager


    async def _make_request(self,
                            method: str,
                            endpoint: str,
                            json_data: Optional[dict] = None,
                            params: Optional[dict] = None,
                            headers: Optional[dict] = None,
                            timeout: int = DEFAULT_TIMEOUT
            ) -> Optional[dict]:
        """
        Выполнение запроса к API GLPI

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: Конечная точка API (например, 'Ticket')
            json_data: Данные для отправки
            timeout: Таймаут запроса в секундах

        Returns:
            Ответ API или None для статуса 204, или НЕТ КОНТЕНТА

        Raises:
            GLPIUnauthorizedError: Если нет сессии
            GLPIAPIError: При ошибках API
            GLPIRequestError: При ошибках соединени
        """

        if not isinstance(method, str) or method.upper() not in {'GET', 'POST', 'PUT', 'DELETE'}:
            raise ValueError(f"Неподдерживаемый HTTP метод: {method}")

        if not endpoint or not isinstance(endpoint, str):
            raise ValueError("Endpoint должен быть непустой строкой")

        if not self.session_manager._session_token:
            raise GLPIUnauthorizedError("Сессия не найдена")

        session = self.session_manager.client_session

        url = f"{self.session_manager.url}/{endpoint}"

        default_headers = {
            'session-token': self.session_manager._session_token,
            'app-token': self.session_manager._app_token,
            **self.BASE_HEADERS
        }
        final_headers = {**default_headers, **(headers or {})}

        try:
            async with session.request(
                    method=method.upper(),
                    url=url,
                    headers=final_headers,
                    json=json_data,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as response:

                    # Обработка пустых ответов
                    if 200 <= response.status < 300:
                        if response.status == 204:
                            print("status: 204")
                            return None

                        try:
                            print(f"response: {await response.json()}")
                            return await response.json()

                        except ContentTypeError:
                            print("status: ContentTypeError")
                            return None

                    # Обработка ошибки
                    error_msg = await self._parse_error_response(response)
                    logger.error(error_msg)
                    raise GLPIAPIError(error_msg, status_code=response.status)

        except aiohttp.ClientError as e:
            logger.exception("Ошибка API запроса")
            raise GLPIRequestError(f"Ошибка API запроса: {str(e)}") from e


    async def _parse_error_response(self, response: aiohttp.ClientResponse) -> str:
        """Парсинг ошибки HTTP для получения деталей"""
        try:
            error_data = await response.json()
            return (
                    f"HTTP Error {response.status}:"
                    f"{error_data.get('message', await response.text())}"
                    )

        except Exception:
            return f"HTTP Error {response.status}: {await response.text()}"


    async def get(self,
                  endpoint: str,
                  params: Optional[dict] = None,
                  headers: Optional[dict] = None,
                  timeout: int = 10
                )-> Optional[dict]:

        return await self._make_request('GET', endpoint, params=params,
                                 headers=headers, timeout=timeout)

    async def post(self,
                   endpoint: str,
                   json_data: Optional[dict],
                   timeout: int = 10
                ) -> Optional[dict]:
        headers = {'Content-Type': 'application/json'}
        return await self._make_request('POST', endpoint, json_data=json_data,
                                 headers=headers, timeout=timeout)

    async def put(self,
                  endpoint: str,
                  json_data: Optional[dict] = None,
                  headers: Optional[dict] = None,
                  timeout: int = 10
                ) -> Optional[dict]:

        return await self._make_request('PUT', endpoint, json_data=json_data,
                                 headers=headers, timeout=timeout)

    async def delete(self,
                     endpoint: str,
                     json_data: Optional[dict],
                     headers: Optional[dict] = None,
                     timeout: int = 10
                ) -> Optional[dict]:

        return await self._make_request('DELETE', endpoint, json_data=json_data,
                                 headers=headers, timeout=timeout)
