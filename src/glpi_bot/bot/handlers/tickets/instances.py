from glpi_bot.bot.handlers.tickets.models.fork_maker import BaseForkMaker
from .models.dynamic_message import DynamicBotMessage
from glpi_bot.bot.keyboards import base_kb, base_buttons


bot_message = DynamicBotMessage(inline_keyboard=base_kb())

incident_1c_fork_maker = BaseForkMaker(base_buttons=base_buttons)
inc_it_fork_maker = BaseForkMaker(base_buttons=base_buttons)
request_it_fork_maker = BaseForkMaker(base_buttons=base_buttons)
req_1c_fork_maker = BaseForkMaker(base_buttons=base_buttons)
