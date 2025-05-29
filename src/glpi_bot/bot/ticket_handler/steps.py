from glpi_bot.bot.ticket_handler.form_framework.step import FormStep

class TypeStep(FormStep):
    key = "type"
    show_key = "Тип заявки"
    prompt = "Выберите тип заявки"

    def kb(self):
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Инцидент", callback_data="type:inc")],
            [InlineKeyboardButton(text="Запрос", callback_data="type:req")],
        ])

    async def handle_input(self, message, state):
        await state.update_data(type=message.text)

class CategoryStep(FormStep):
    key = "category"
    show_key = "Категория"
    prompt = "Выберите категорию"

    def kb(self):
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Сеть", callback_data="cat:net")],
            [InlineKeyboardButton(text="ПО", callback_data="cat:sw")],
        ])

    async def handle_input(self, message, state):
        await state.update_data(category=message.text)


