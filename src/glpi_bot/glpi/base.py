# glpi/base.py

import logging
import requests
from typing import Optional
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

    def _make_request(self,
                     method: str,
                     endpoint: str,
                     json_data: Optional[dict] = None,
                     params: Optional[dict] = None,
                     headers: Optional[dict] = None,
                     timeout: int = 10) -> Optional[dict]:
        """
        Выполнение запроса к API GLPI

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: Конечная точка API (например, 'Ticket')
            json_data: Данные для отправки
            timeout: Таймаут запроса в секундах

        Returns:
            Ответ API или None для статуса 204

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

        url = f"{self.session_manager.url}/{endpoint}"

        default_headers = {
            'session-token': self.session_manager._session_token,
            'app-token': self.session_manager._app_token,
            **self.BASE_HEADERS
        }
        final_headers = {**default_headers, **(headers or {})}

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=final_headers,
                json=json_data,
                params=params,
                timeout=timeout
            )

            # Обработка 204 no Content
            if response.status_code == 204:
                return None

            response.raise_for_status()

            # Обработка пустого ответа
            if not response.text.strip():
                return None

            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = self._parse_error_response(e)
            logger.error(error_msg)
            raise GLPIAPIError(error_msg, getattr(e.response, 'status_code', None)) from e

        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка API запроса: {str(e)}"
            logger.error(error_msg)
            raise GLPIRequestError(error_msg) from e

    def _parse_error_response(self, error: requests.exceptions.HTTPError) -> str:
        """Парсинг ошибки HTTP для получения деталей"""
        try:
            if error.response is None:
                return f"HTTP Error: {str(error)}"

            error_data = error.response.json()
            return (f"HTTP Error {error.response.status_code}: "
                    f"{error_data.get('message', error.response.text)}")
        except ValueError:
            return f"HTTP Error {error.response.status_code}: {error.response.text}"


    def get(self,
            endpoint: str,
            params: Optional[dict] = None,
            headers: Optional[dict] = None,
            timeout: int = 10) -> Optional[dict]:

        return self._make_request('GET', endpoint, params=params, headers=headers,
                                 timeout=timeout)

    def post(self,
             endpoint: str,
             json_data: Optional[dict],
             timeout: int = 10) -> Optional[dict]:
        headers = {'Content-Type': 'application/json'}

        return self._make_request('POST', endpoint, json_data=json_data,
                                 headers=headers, timeout=timeout)

    def put(self,
            endpoint: str,
            json_data: Optional[dict] = None,
            headers: Optional[dict] = None,
            timeout: int = 10) -> Optional[dict]:

        return self._make_request('PUT', endpoint, json_data=json_data,
                                 headers=headers, timeout=timeout)

    def delete(self,
               endpoint: str,
               json_data: Optional[dict],
               headers: Optional[dict] = None,
               timeout: int = 10) -> Optional[dict]:

        return self._make_request('DELETE', endpoint, json_data=json_data,
                                 headers=headers, timeout=timeout)
