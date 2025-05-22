# glpi/base.py

import logging
import requests
from typing import Optional
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class GLPIConnection:
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


