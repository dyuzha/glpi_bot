# from glpi_bot.bot.handlers.tickets import inc_it_fork_maker
# from .inc_it import inet_truble, mail_truble, rdp_truble
# from .inc_it import call_title

from .inc_it import build_flow as build_flow_inc_it
from .inc_1c import build_flow as build_flow_inc_1c
from .req_1c import build_flow as build_flow_req_1c
from .req_it import build_flow as build_flow_req_it

__all__=[
        "build_flow_inc_it",
        "build_flow_inc_1c",
        "build_flow_req_it",
        "build_flow_req_1c"
        ]
