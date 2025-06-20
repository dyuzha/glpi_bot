import time
from abc import ABC, abstractmethod
from typing import Optional

class BaseCache(ABC):
    """
    Абстрактный базовый класс для реализации кеша с TTL (Time To Live).

    Логика:
    - Данные кешируются в памяти.
    - Метод get() проверяет TTL и вызывает загрузку через load(),
    который должен быть реализован в подклассе.
    - refresh() принудительно обновляет кеш.
    - invalidate() сбрасывает кеш.
    """

    def __init__(self, ttl_seconds: Optional[int] = None):
        """
        :param ttl_seconds: Время жизни кеша в секундах (TTL).
                            По истечении этого времени данные будут обновлены
                            при следующем запросе.
        """
        self._data = None
        self._timestamp = 0
        self.ttl = ttl_seconds

    def get(self, *args, **kwargs):
        """Возвращает кешированные данные, обновляя при необходимости"""
        now = time.time()

        if self._data is None:
            self._data = self.load(*args, **kwargs)
            self._timestamp = now

        elif self.ttl is not None and (now - self._timestamp) > self.ttl:
            self._data = self.load(*args, **kwargs)
            self._timestamp = now

        return self._data

    def refresh(self):
        """Принудительно обновляет данные из источника."""
        self._data = self.load()
        self._timestamp = time.time()

    def invalidate(self):
        """Сбрасывает кеш, очищая данные."""
        self._data = None
        self._timestamp = 0

    @abstractmethod
    def load(self) -> dict:
        """Метод для переопределения в наследниках — загрузка данных"""
        ...
