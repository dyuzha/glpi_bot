from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать заявку")],
            # [KeyboardButton(text="Мои заявки")]
        ],
        resize_keyboard=True
    )

def back_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отмена"), KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def confirm_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Подтвердить")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )

def type_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Инцидент"), KeyboardButton(text="Запрос")],
            [KeyboardButton(text="❌ Отмена"), KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True
    )

def auth_code_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Изменить логин"), KeyboardButton(text="Отправить код повторно")],
        ],
        resize_keyboard=True
    )

def auth_login_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Изменить логин")],
        ],
        resize_keyboard=True
    )

def succ_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Перейти в главное меню")],
        ],
        resize_keyboard=True
    )
