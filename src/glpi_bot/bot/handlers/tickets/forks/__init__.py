from glpi_bot.bot.handlers.tickets import inc_it_fork_maker
from .inc_it import inet_truble, mail_truble, rdp_truble
from .inc_it import deffault_call_title as call


# Регистрация дефолтных обаботчиков
inc_it_fork_maker.register_many(
    [
        # ("key", "button_text", func),
        ("no_inet", "Нет интернета", inet_truble),
        ("invalid_mail", "Не работает почта", mail_truble),
        ("rdp", "Проблема с RDP", rdp_truble),
        ("office", "Проблема c офисными программами", call,
         {"category": "Проблема при работе с офисными программами"}),
    ],
)

