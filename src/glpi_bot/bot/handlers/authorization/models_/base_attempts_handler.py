# base_attempts_handler.py

from datetime import datetime, timedelta
from typing import Optional
import logging


logger = logging.getLogger(__name__)


class MaxAttempts(Exception):
    """Превышено максимальное количество попыток"""
    def __init__(
        self,
        remaining_blocked_time: Optional[timedelta] = None,
        attempts_made: Optional[int] = None,
        max_attempts: Optional[int] = None
    ):
        self.remaining_blocked_time = remaining_blocked_time
        self.attempts_made = attempts_made
        self.max_attempts = max_attempts

        message = f"Превышено максимальное количество попыток ({attempts_made}/{max_attempts})."
        if remaining_blocked_time:
            message += f" Блокировка ещё на {remaining_blocked_time}."
        super().__init__(message)


class BaseAttemptsHandler:

    def __init__(self, max_attempts: int, break_after_limit: timedelta):
        self._max_attempts = max_attempts
        self._break_after_limit = break_after_limit
        self._attempts: int = 0
        self._attempts_blocked_until: Optional[datetime] = None


    @property
    def remaining_blocked_time(self) -> Optional[timedelta]:
        """Оставшиеся время блокировки"""
        if self._attempts_blocked_until:
            remaining_time = self._attempts_blocked_until - datetime.now()

            if remaining_time < timedelta(0):
                self._attempts = 0
                self._attempts_blocked_until = None
                return None
            return remaining_time
        return None


    @property
    def remaining_attempts(self) -> int:
        """Оставшиеся попытки"""
        return max(self._max_attempts - self._attempts, 0)


    def attempt(self) -> bool:
        """
        Выполняет одну попытку действия. Отслеживает количество попыток и применяет блокировку при превышении лимита.

        Поведение:
        - Если в текущий момент действует блокировка (не истекло `remaining_blocked_time`),
        возбуждает исключение `MaxAttempts`, в котором содержится оставшееся время блокировки.

        - Если попытки разрешены, увеличивает счётчик (`_attempts`).

        - При достижении максимального количества попыток (`_max_attempts`),
          устанавливает время блокировки (`_attempts_blocked_until`).

        Исключения:
            MaxAttempts: если пользователь заблокирован.
                         Атрибут `remaining_blocked_time` указывает оставшееся время до разблокировки.
                         Атрибут `attempts_made` указывает выполненные попытки.
                         Атрибут `max_attempts` максимально допустимое количество попыток.

        Returns:
            bool: True, если попытка разрешена.
        """
        blocked_time = self.remaining_blocked_time

        if blocked_time:
            raise MaxAttempts(
                    remaining_blocked_time=blocked_time,
                    attempts_made=self._attempts,
                    max_attempts=self._max_attempts
            )

        self._attempts += 1

        if self._attempts >= self._max_attempts:
            self._attempts_blocked_until = datetime.now() + self._break_after_limit

        return True
