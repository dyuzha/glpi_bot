# glpi/service.py

import logging
import requests
from typing import Optional
from datetime import datetime, timedelta
from glpi import GLPIContextManager


logger = logging.getLogger(__name__)


class GLPIInterface:
    def __init__(self, session_manager: GLPIContextManager):
        self.session_manager = session_manager

    def _make_request(self, method: str, endpoint: str, json_data: dict = None):
        """
        Выполнение запроса к API GLPI
        :param method: HTTP метод (GET, POST, PUT, DELETE)
        :param endpoint: Конечная точка API (например, 'Ticket')
        :param json_data: Данные для отправки (уже должны быть в формате {'input': {...}})
        :return: Ответ API
        """
        if not self.session_manager.glpi_base.session_token:
            raise ConnectionError("Сессия не открыта")

        url = f"{self.session_manager.glpi_base.url}/{endpoint}"
        headers = {
            'Session-Token': self.session_manager.glpi_base.session_token,
            'App-Token': self.session_manager.glpi_base.app_token,
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


# glpi/models.py

import logging
from .api import GLPIConnection
from typing import Optional


logger = logging.getLogger(__name__)


class GLPIUser:
    def __init__(self, **kwargs):
        self.login = kwargs['1']
        self.id = kwargs['2']
        self.organisation = kwargs['3']

    def get_id(self) -> int:
        return self.id

    def get_id_company(self) -> int:
        ...


