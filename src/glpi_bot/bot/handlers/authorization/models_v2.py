# bot/handlers/authorization/models_v2.py

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import logging


logger = logging.getLogger(__name__)




class DeffaultHandler:
    max_attempts: int = 3
    break_between_attempts: Optional[datetime] = None
    break_after_limit: Optional[datetime] = None

    attempts: int = 0
    attempt_blocked_until: Optional[datetime] = None
    attempts_blocked_until: Optional[datetime] = None


    def __init__(self):
        pass


    def __




class CodeHandler:
    max_attempts: int = 3
    break_between_attempts: int = 3
    break_after_block_attemtps: int = 3
    break_between_request: int = 3


class LoginHandler:
    max_attempts: int = 3
    break_between_attempts: int = 3
    break_after_block_attemtps: int = 3
