# glpi/models.py

import logging
import requests
from typing import Optional
from glpi_bot.glpi import GLPIBase


logger = logging.getLogger(__name__)


class GLPIUser:
    def __init__(self, **kwargs):
        self._login = kwargs['1']
        self.id = kwargs['2']
        self.organisation = kwargs['3']

    def __repr__(self):
        return f"GLPIUser -- <{self.id}> -- <{self._login}> -- <{self.organisation}>"


class GLPIInterface(GLPIBase):

    def create_ticket(self, **data) -> dict:
        """Создание заявки"""
        ticket_data = {"input": data}
        return self.post(endpoint="Ticket", json_data=ticket_data)

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

        responce = self.post(endpoint="search/User", json_data=data)
        logger.info(f"responce: {responce}")
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

    def get_all_users(self, range_limit: str = "0-1000") -> list:
        """
        Получение списка всех пользователей GLPI

        :param range_limit: Ограничение диапазона (например "0-1000")
        :return: Список пользователей
        """
        search_params = {
            "forcedisplay": [1, 2, 3],  # ID, Логин, Имя (номера полей)
            "range": range_limit,
            "sort": 1,  # Сортировка по ID
            "order": "ASC"
        }

        try:
            response = self.post(endpoint="search/User", json_data=search_params)
        except Exception as e:
            logger.error(f"Ошибка при получении списка пользователей: {e}")
            raise
        else:
            users = response['data']
            return [GLPIUser(**user) for user in users]

    def get_all_entities(self) -> dict:
        """
        Получение списка всех организаций (entities) из GLPI
        Возвращает список словарей с id и названиями организаций
        """
        search_params = {
            "forcedisplay": [1, 2],  # 1 - ID, 2 - название
            "range": "0-1000",       # Лимит записей (можно увеличить)
            "sort": 1,               # Сортировка по ID
            "order": "ASC"           # По возрастанию
        }

        try:
            response = self.post(endpoint="search/Entity", json_data=search_params)
            return {
                entity["1"].rsplit("> ", 1)[-1]: entity["2"]
                for entity in response.get('data', [])
            }
        except Exception as e:
            logger.error(f"Ошибка при получении списка организаций: {e}")
            raise

    def assign_ticket(self, ticket_id: int, user_id: int):
        """Назначение заявки на пользователя"""
        # data = {
        #     "input": {
        #         "_users_id_assign": user_id
        #     }
        # }
        # return self.conn.make_request("PUT", f"Ticket/{ticket_id}", json=data)
        pass
