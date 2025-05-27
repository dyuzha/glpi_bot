# glpi/base.py

import logging
import requests
from typing import Optional
from glpi_bot.glpi.session import GLPISessionManager


logger = logging.getLogger(__name__)


class GLPIBase:
    """Базовый класс для работы с GLPI API"""

    def __init__(self, session_manager: GLPISessionManager):
        self.session_manager = session_manager

    def _make_request(self,
                     method: str,
                     endpoint: str,
                     json_data: Optional[dict] = None,
                     params: Optional[dict] = None,
                     headers: Optional[dict] = None,
                     timeout: int = 10) -> dict:
        """
        Выполнение запроса к API GLPI
        :param method: HTTP метод (GET, POST, PUT, DELETE)
        :param endpoint: Конечная точка API (например, 'Ticket')
        :param json_data: Данные для отправки
        :param timeout: Таймаут запроса в секундах
        :return: Ответ API
        :raises: ConnectionError при ошибках соединения или API
        """
        if not self.session_manager._session_token:
            raise ConnectionError("Сессия не найдена")

        url = f"{self.session_manager.url}/{endpoint}"

        deffault_headers = {
            'session-token': self.session_manager._session_token,
            'app-token': self.session_manager._app_token,
        }
        final_headers = {**deffault_headers, **(headers or {})}

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
                raise Exception("No Content")

            response.raise_for_status()

            # Обработка пустого ответа
            if not response.text.strip():
                raise Exception("Null response")

            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = self._parse_error_response(e)
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка API запроса: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError() from e

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
            timeout: int = 10) -> dict:

        return self._make_request('GET', endpoint, params=params, headers=headers,
                                 timeout=timeout)

    def post(self,
             endpoint: str,
             json_data: Optional[dict],
             timeout: int = 10) -> dict:
        headers = {'Content-Type': 'application/json'}

        return self._make_request('POST', endpoint, json_data=json_data,
                                 headers=headers, timeout=timeout)

    def put(self,
            endpoint: str,
            json_data: Optional[dict] = None,
            headers: Optional[dict] = None,
            timeout: int = 10) -> dict:

        return self._make_request('PUT', endpoint, json_data=json_data,
                                 headers=headers, timeout=timeout)

    def delete(self,
               endpoint: str,
               json_data: Optional[dict],
               headers: Optional[dict] = None,
               timeout: int = 10) -> dict:

        return self._make_request('DELETE', endpoint, json_data=json_data,
                                 headers=headers, timeout=timeout)
