# bot/handlers/tickets/handlers/steps/title_step.py

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from glpi_bot.bot.handlers.tickets.models.dinamic_bod_message import DynamicBotMessage
from glpi_bot.bot.handlers.tickets.models.text_input_step import TextInputStep
from glpi_bot.bot.states import FinalStates


async def validate(message: Message,
                   state: FSMContext,
                   bot_message: DynamicBotMessage,
                   length: int = 10
                         ) -> bool:
    text = message.text.strip()
    if len(text) < length:
        await bot_message.update_message(message, state,
            f"❗ Описание:\n{text} — слишком короткий"
            f"Описание должно содержать минимум {length} символов"
        )
        await message.delete()
        return False
    return True


async def save(message: Message,
               state: FSMContext,
               bot_message: DynamicBotMessage):
    text = message.text.strip()
    await message.delete()
    await state.update_data(description=text)
    await bot_message.add_field(state, "Описание", text)


bot_message = DynamicBotMessage()


description_step = TextInputStep(
    state=FinalStates.description,
    prompt="💬 Опишите проблему более подробно",
    bot_message=bot_message,
    validate=validate,
    final=save
    )
