from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from glpi_bot.bot.handlers.tickets.models.dinamic_bod_message import DynamicBotMessage
from glpi_bot.bot.handlers.tickets.models.text_input_step import TextInputStep
from glpi_bot.bot.states import FinalStates


async def validate_title(msg: Message, state: FSMContext, bot_message: DynamicBotMessage) -> bool:
    await msg.delete()
    text = msg.text.strip()
    if len(text) < 10:
        await bot_message.update_message(msg, state,
            f"❗ Заголовок:\n{text} — слишком короткий\nМинимум 10 символов"
        )
        return False
    return True


async def save_title(msg: Message, state: FSMContext, bot_message: DynamicBotMessage):
    await msg.delete()
    text = msg.text.strip()
    await state.update_data(title=text)
    await bot_message.add_field(state, "Заголовок", text)
    await bot_message.update_message(msg, state)  # можно текст не передавать — будет отрендерен сам


bot_message = DynamicBotMessage()


title_step = TextInputStep(
    state=FinalStates.title,
    prompt="Введи title",
    bot_message=bot_message,
    validate=validate_title,
    final=save_title)
