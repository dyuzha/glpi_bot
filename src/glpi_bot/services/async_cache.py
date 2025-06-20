import time
from abc import ABC, abstractmethod
from typing import Optional, Any
import asyncio


class AsyncBaseCache(ABC):
    """
    Асинхронный базовый класс для реализации кеша с TTL (Time To Live).

    Логика:
    - Данные кешируются в памяти.
    - Метод get() проверяет TTL и вызывает асинхронную загрузку через load(),
    если нужно.
    - refresh() принудительно обновляет кеш.
    - invalidate() сбрасывает кеш.
    """

    def __init__(self, ttl_seconds: Optional[int] = None):
        """
        :param ttl_seconds: Время жизни кеша в секундах (TTL).
                            По истечении этого времени данные будут обновлены
                            при следующем запросе.
        """
        self._data: Optional[Any] = None
        self._timestamp: float = 0
        self.ttl: Optional[int] = ttl_seconds
        self._lock = asyncio.Lock()


    async def get(self, *args, **kwargs) -> Any:
        """Асинхронно возвращает данные из кеша, обновляя их при необходимости"""
        now = time.time()

        async with self._lock:
            if self._data is None:
                self._data = await self.load(*args, **kwargs)
                self._timestamp = now

            elif self.ttl is not None and (now - self._timestamp) > self.ttl:
                self._data = await self.load(*args, **kwargs)
                self._timestamp = now

        return self._data


    async def refresh(self, *args, **kwargs) -> None:
        """Принудительно обновляет кеш."""
        async with self._lock:
            self._data = await self.load(*args, **kwargs)
            self._timestamp = time.time()

    async def invalidate(self) -> None:
        """Очищает кеш."""
        async with self._lock:
            self._data = None
            self._timestamp = 0

    @abstractmethod
    async def load(self, *args, **kwargs) -> Any:
        """Асинхронный метод загрузки данных. Должен быть реализован в наследниках."""
        ...
