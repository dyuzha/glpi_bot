from aiogram.fsm.state import State, StatesGroup
import logging


logger = logging.getLogger(__name__)  # Используем __name__ для автоматического определения имени модуля

class BaseStates(StatesGroup):
    waiting_autorisation = State()
    complete_autorisation = State()

class AuthStates(StatesGroup):
    LOGIN = State()
    LOGIN_HANDLER = State()
    CODE = State()
    CODE_HANDLER = State()
    SUCCESS = State()

class TicketStates(StatesGroup):
    type = State()
    category = State()
    incident = State()
    request = State()

class OneCStates(StatesGroup):
    inc_1c = State()

class FinalStates(StatesGroup):
    description = State()
    title = State()
    confirm = State()
