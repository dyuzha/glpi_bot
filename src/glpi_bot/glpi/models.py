# glpi/models.py

import logging
import requests
from typing import Optional
from glpi_bot.glpi import GLPIBase


logger = logging.getLogger(__name__)


class GLPIUser:
    def __init__(self, **kwargs):
        self._login = kwargs['1']
        self._id = kwargs['2']
        self._organisation = kwargs['3']

    @property
    def id(self) -> int:
        return self._id

    @property
    def id_organisation(self) -> int:
        ...


class GLPIInterface(GLPIBase):
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
                    "searchtype": "contains",
                    "value": login  # Пустое значение = все записи
                }
            ],
            "forcedisplay": [1, 2, 3],  # Минимальный набор полей
            "range": "0-1000",
        }

        responce = self.make_request("POST", "search/User", json_data=data)
        print("responce: ", responce)
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
