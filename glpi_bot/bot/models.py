from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


LOGIN_MAX_ATTEMPTS = 3              # Макс. число попыток
LOGIN_TIMEOUT_AFTER_LIMIT = 30      # Блокировка после превышения (сек)
# LOGIN_REQUEST_TIMEOUT = 5         # Таймаут между запросами (сек)

CODE_MAX_ATTEMPTS = 3               # Макс. число попыток
CODE_TIMEOUT_AFTER_LIMIT = 20       # Блокировка после превышения (сек)
CODE_REQUEST_TIMEOUT = 60           # Таймаут между запросами (сек)
CODE_LIFE_TIME = 120                # Время действия кода


@dataclass
class TimeHandler:
    max_attempts: int = 3               # Макс. число попыток
    timeout_after_limit: int = 300      # Блокировка после превышения (сек)
    request_timeout: int = 60           # Таймаут между запросами (сек)

    attempts: int = 0                   # Текущие попытки
    last_request_time: Optional[datetime] = None
    blocked_until: Optional[datetime] = None

    def can_make_request(self) -> bool:
        """Можно ли отправить запрос (учитывая таймаут и блокировку)"""
        if self.blocked_until and datetime.now() < self.blocked_until:
            return False
        if self.last_request_time is None:
            return True

        # Если в данном экземпляре не выставлена задержка между запросами
        if self.request_timeout is None:
            return (datetime.now() - self.last_request_time).seconds >= self.request_timeout
        else:
            return True

    def add_attempt(self) -> bool:
        """Увеличивает счетчик попыток. Возвращает False, если достигнут лимит."""
        self.attempts += 1
        if self.attempts >= self.max_attempts:
            self.blocked_until = datetime.now() + timedelta(seconds=self.timeout_after_limit)
            self.attempts = 1
            return False
        return True

    def reset(self):
        """Сброс всех ограничений (после успешного действия)"""
        self.attempts = 0
        self.blocked_until = None
        self.last_request_time = None

    def get_remaining_time(self) -> int:
        """Оставшееся время блокировки (сек)"""
        if not self.blocked_until:
            return 0
        return max(0, int((self.blocked_until - datetime.now()).total_seconds()))


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
        # request_timeout=LOGIN_REQUEST_TIMEOUT
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
