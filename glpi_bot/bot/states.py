from aiogram.fsm.state import State, StatesGroup
import logging


logger = logging.getLogger(__name__)  # Используем __name__ для автоматического определения имени модуля

class BaseStates(StatesGroup):
    WAITING_AUTORISATION = State()
    COMPLETE_AUTORISATION = State()

class TicketCreation(StatesGroup):
    waiting_for_type = State()
    waiting_for_title = State()
    waiting_for_description = State()
    confirm_data = State()

class AuthStates(StatesGroup):
    LOGIN = State()
    LOGIN_HANDLER = State()
    CODE = State()
    CODE_HANDLER = State()
    SUCCESS = State()
