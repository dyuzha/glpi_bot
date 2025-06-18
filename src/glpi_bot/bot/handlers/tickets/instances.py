from glpi_bot.bot.handlers.models.dynamic_message import DynamicBotMessage
from glpi_bot.bot.keyboards import base_kb


bot_message = DynamicBotMessage(inline_keyboard=base_kb())
