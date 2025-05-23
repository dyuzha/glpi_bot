from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)


LOGIN_MAX_ATTEMPTS = 3              # Макс. число попыток
LOGIN_TIMEOUT_AFTER_LIMIT = 10      # Блокировка после превышения (сек)
# LOGIN_REQUEST_TIMEOUT = 5         # Таймаут между запросами (сек)

CODE_MAX_ATTEMPTS = 3               # Макс. число попыток
CODE_TIMEOUT_AFTER_LIMIT = 10       # Блокировка после превышения (сек)
CODE_REQUEST_TIMEOUT = 60           # Таймаут между запросами (сек)
CODE_LIFE_TIME = 120                # Время действия кода


@dataclass
class TimeHandler:
    max_attempts: int = 3               # Макс. число попыток
    timeout_after_limit: int = 300      # Блокировка после превышения (сек)
    request_timeout: int = 60           # Таймаут между запросами (сек)

    attempts: int = 0                   # Текущие попытки
    last_request_time: Optional[datetime] = None
    attempts_blocked_until: Optional[datetime] = None
    # request_blocked_until: Optional[datetime] = None

    def get_blocked_request_time(self):
        """Можно ли отправить запрос (учитывая таймаут и блокировку)"""
        # Если нет блокировки
        if self.last_request_time is None:
            return 0
        past_time = datetime.now() - self.last_request_time
        remaining_time = timedelta(seconds=self.request_timeout) - past_time
        return max(0, int(remaining_time.total_seconds()))


    # def set_request_blocked_until(self) -> int:
    #     if self.request_blocked_until is None:
    #         raise ValueError("Параметр request_blocked_until не задан!")
    #
    #     self.attempts_blocked_until = datetime.now() + timedelta(seconds=self.request_timeout)
    #     return self.request_timeout


    def set_attempts_blocked_until(self) -> int:
        """Выставление блокировки на попытки"""
        # if self.attempts_blocked_until is None:
        #     logger.debug(f"Параметр attempts_blocked_until не задан")
        #     raise ValueError("Параметр attempts_blocked_until не задан!")
        self.attempts_blocked_until = datetime.now() + timedelta(seconds=self.timeout_after_limit)
        logger.debug(f"SET attempts_blocked_until:{self.attempts_blocked_until}")
        self.attempts = 0
        logger.debug(f"SET attempts: {self.attempts}")
        return self.timeout_after_limit


    def add_attempt(self):
        """Увеличивает счетчик попыток. Возвращает False, если достигнут лимит."""
        self.attempts += 1
        # if self.attempts >= self.max_attempts:
        #     self.blocked_until = datetime.now() + timedelta(seconds=self.timeout_after_limit)
        #     self.attempts = 0
        #     return False
        # return True

    @property
    def remaining_attempts(self) -> int:
        if self.attempts_blocked_until is not None and datetime.now() < self.attempts_blocked_until:
            return 0
        return self.max_attempts - self.attempts


    def reset(self):
        """Сброс всех ограничений (после успешного действия)"""
        self.attempts = 0
        self.attempts_blocked_until = None
        self.last_request_time = None

    def get_blocked_attempts_time(self) -> int:
        """Оставшееся время блокировки (сек)"""
        if not self.attempts_blocked_until:
            return 0
        return max(0, int((self.attempts_blocked_until - datetime.now()).total_seconds()))


@dataclass
class AuthState:
    login: Optional[str] = None
    mail: Optional[str] = None
    code: Optional[str] = None
    code_life_time: int = CODE_LIFE_TIME

    login_handler: TimeHandler = field(
        default_factory=lambda: TimeHandler(
        max_attempts=LOGIN_MAX_ATTEMPTS,
        timeout_after_limit=LOGIN_TIMEOUT_AFTER_LIMIT,
    ))

    code_handler: TimeHandler = field(
        default_factory=lambda: TimeHandler(
        max_attempts=CODE_MAX_ATTEMPTS,
        timeout_after_limit=CODE_TIMEOUT_AFTER_LIMIT,
        request_timeout=CODE_REQUEST_TIMEOUT,
    ))

    def is_code_valid(self) -> bool:
        """Проверяет не истекло ли время действия кода"""
        if self.code_handler.last_request_time is None:
            return False

        elapsed = (datetime.now() - self.code_handler.last_request_time).total_seconds()
        return elapsed < self.code_life_time

    def reset(self):
        """Сброс всей авторизации"""
        self.login = None
        self.mail = None
        self.code = None
        self.login_handler.reset()
        self.code_handler.reset()
