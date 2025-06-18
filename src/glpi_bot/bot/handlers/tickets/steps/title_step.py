# bot/handlers/tickets/handlers/steps/title_step.py

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from glpi_bot.bot.handlers.models import DynamicBotMessage
from glpi_bot.bot.handlers.models import TextInputStep
from glpi_bot.bot.handlers.tickets.instances import bot_message
from glpi_bot.bot.states import FinalStates


async def validate(message: Message,
                   state: FSMContext,
                   bot_message: DynamicBotMessage,
                   length: int = 10
                         ) -> bool:
    text = message.text.strip()
    if len(text) < length:
        await bot_message.flasher.warning(message, state,
            f"Заголовок:\n{text} — слишком короткий"
            f"Заголовок должен содержать минимум {length} символов"
        )
        await message.delete()
        return False
    return True


async def save(message: Message,
               state: FSMContext,
               bot_message: DynamicBotMessage):

    text = message.text.strip()
    await message.delete()
    await state.update_data(title=text)
    await bot_message.add_field(state, "Заголовок", text)


title_step = TextInputStep(
    state=FinalStates.title,
    prompt="Введи title",
    bot_message=bot_message,
    validate=validate,
    final=save
    )
