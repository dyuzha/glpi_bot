# glpi/models.py

import logging
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

    async def create_ticket(self, **data) -> Optional[dict]:
        """Создание заявки"""
        ticket_data = {"input": data}
        return await self.post(endpoint="Ticket", json_data=ticket_data)

    async def get_user(self, login: str) -> Optional[GLPIUser]:
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

        responce = await self.post(endpoint="search/User", json_data=data)

        if responce is None:
            return None

        if responce.get('totalcount', 0) == 0:
            return None

        # Отфильтровываю вывод до полного совпадения (костыль)
        users = responce['data']
        for user in users:
            if user["1"] == login:
                return GLPIUser(**user)

        return None


    async def get_all_users(self, range_limit: str = "0-1000") -> list[GLPIUser]:
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
            response = await self.post(
                    endpoint="search/User",
                    json_data=search_params
                    )

            if response is None:
                raise ValueError("Ответ от GLPI API - None")

        except Exception as e:
            logger.error(f"Ошибка при получении списка пользователей: {e}")
            raise

        users = response.get('data', [])
        return [GLPIUser(**user) for user in users]


    async def get_all_entities(self) -> dict[str, str]:
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
            response = await self.post(endpoint="search/Entity", json_data=search_params)
            return {
                entity["1"].rsplit("> ", 1)[-1]: entity["2"]
                for entity in response.get('data', [])
            }
        except Exception as e:
            logger.error(f"Ошибка при получении списка организаций: {e}")
            raise
