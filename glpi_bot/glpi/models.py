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


class GLPIService(GLPIConnection):
    """Сервис для взаимодействия с GLPI"""

    def create_ticket(self, **data) -> dict:
        """Создание заявки"""
        ticket_data = {"input": data}
        return self._make_request("POST", "Ticket", json_data=ticket_data)

    def get_user(self, login: str) -> Optional[GLPIUser]:
        """Получение пользователя GLPI"""
        # Использую contains потомучто equals не работает
        data = {
            "criteria": [
                {
                    "field": "1",
                    "searchtype": "contains",
                    "value": login,
                    "forcedisplay": "id"
                },
            ],
            "forcedisplay": ["1", "2", "3"]
        }

        responce = self._make_request("POST", "search/User", json_data=data)
        if responce['totalcount'] == 0:
            return None

        # Отфильтровываю вывод до полного совпадения (костыль)
        users = responce['data']
        for user in users:
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

    def create_ticket(self, **data):
        user = self.get_user(data["login"])
        if user is None:
            raise ValueError
        else: del data["login"]

        # Получаем id автора заявки
        user_id = user.get_id()
        # Выставляем его id в инициаторы заявки
        data["_users_id_requester"] = user_id

        # Делаем источник заявки - телеграмм
        data["requesttypes_id"] = 14

        return super().create_ticket(**data)
