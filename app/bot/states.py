from aiogram.fsm.state import State, StatesGroup
import logging


logger = logging.getLogger(__name__)  # Используем __name__ для автоматического определения имени модуля

class Base(StatesGroup):
    no_authorization = State()
    authorization = State()

class TicketCreation(StatesGroup):
    waiting_for_type = State()
    waiting_for_title = State()
    waiting_for_description = State()
    confirm_data = State()

class Authorization(StatesGroup):
    waiting_for_login = State()
    waiting_for_code = State()
