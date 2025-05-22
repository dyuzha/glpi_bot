# services/glpi_service.py

import logging
import requests
from typing import Optional
from datetime import datetime, timedelta
from glpi import GLPIInterface, GLPIUser, GLPISessionManager


logger = logging.getLogger(__name__)


class GLPIService(GLPIInterface):
    """Сервис для взаимодействия с GLPI"""
    def create_ticket(self, **data) -> dict:
        """Создание заявки"""
        ticket_data = {"input": data}
        return self.make_request("POST", "Ticket", json_data=ticket_data)

    def get_user(self, login: str) -> Optional[GLPIUser]:
        """Получение пользователя GLPI"""
        # Использую contains потомучто equals не работает
        data = {
            "criteria": [
                {
                    "field": 1,  # Обязательно должен быть хотя бы один критерий
                    "searchtype": "equals",
                    "value": login  # Пустое значение = все записи
                }
            ],
            "forcedisplay": [1, 2, 3],  # Минимальный набор полей
            "range": "0-1000",
        }

        responce = self.make_request("POST", "search/User", json_data=data)
        if responce['totalcount'] == 0:
            return None

        # Отфильтровываю вывод до полного совпадения (костыль)
        print(responce)
        users = responce['data']
        # print(users)
        for user in users:
            print(user)
            if user["1"] == login:
                return GLPIUser(**user)
        return None

    def assign_ticket(self, ticket_id: int, user_id: int):
        """Назначение заявки на пользователя"""
        # data = {
        #     "input": {
        #         "_users_id_assign": user_id
        #     }
        # }
        # return self.conn.make_request("PUT", f"Ticket/{ticket_id}", json=data)
        pass


class TicketBuilder(GLPIService):
    """Класс для составления заявок"""
    # Пробросить id источника запросов в конфиг

    def __init__(self, session_manager: GLPISessionManager):
        self.session_manager = session_manager

    def create_ticket(self, **data):
        # Получаем пользователя glpi
        with self.session_manager.get_session() as session:
            user = self.get_user(data["login"])
        if user is None:
            raise ValueError

        # Получаем id автора заявки
        user_id = user.get_id()

        # Выставляем его id в инициаторы заявки
        data["_users_id_requester"] = user_id

        # Делаем источник заявки - телеграмм
        data["requesttypes_id"] = 14

        # Убираем login из входных данных
        del data["login"]

        # Создаем тикет с обновленными данными
        return super().create_ticket(**data)
