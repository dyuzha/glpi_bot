# test_base_attempts_handler.py

import pytest
from datetime import timedelta

from .base_attempts_handler import BaseAttemptsHandler, MaxAttempts


def test_successful_attempts_within_limit():
    handler = BaseAttemptsHandler(max_attempts=3, break_after_limit=timedelta(seconds=10))

    for _ in range(3):
        assert handler.attempt() is True

    assert handler.remaining_attempts == 0


def test_exceeding_max_attempts_raises_exception():
    handler = BaseAttemptsHandler(max_attempts=2, break_after_limit=timedelta(seconds=5))

    handler.attempt()
    handler.attempt()

    with pytest.raises(MaxAttempts) as exc_info:
        handler.attempt()

    exc = exc_info.value
    assert isinstance(exc.remaining_blocked_time, timedelta)
    assert exc.attempts_made == 2
    assert exc.max_attempts == 2


def test_block_resets_after_time():
    handler = BaseAttemptsHandler(max_attempts=1, break_after_limit=timedelta(seconds=0.1))

    handler.attempt()

    # заблокировано
    with pytest.raises(MaxAttempts):
        handler.attempt()

    # подождём до разблокировки
    import time
    time.sleep(0.2)

    assert handler.attempt() is True  # снова работает
    assert handler.remaining_attempts == 0


def test_remaining_attempts_property():
    handler = BaseAttemptsHandler(max_attempts=4, break_after_limit=timedelta(seconds=10))

    assert handler.remaining_attempts == 4
    handler.attempt()
    assert handler.remaining_attempts == 3
    handler.attempt()
    assert handler.remaining_attempts == 2


def test_blocked_time_none_if_not_blocked():
    handler = BaseAttemptsHandler(max_attempts=3, break_after_limit=timedelta(seconds=5))

    assert handler.remaining_blocked_time is None
    handler.attempt()
    assert handler.remaining_blocked_time is None


def test_blocked_time_is_none_after_expired():
    handler = BaseAttemptsHandler(max_attempts=1, break_after_limit=timedelta(milliseconds=50))
    handler.attempt()

    with pytest.raises(MaxAttempts):
        handler.attempt()

    import time
    time.sleep(0.1)

    # должно сброситься
    assert handler.remaining_blocked_time is None
    assert handler.attempt() is True
