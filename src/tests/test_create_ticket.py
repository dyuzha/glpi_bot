from glpi_bot.glpi import GLPISessionManager
from glpi_bot.services import GLPITicketManager
from glpi_bot.config_handlers import GLPI_DATA


# Инициализация glpi
glpi_session_manager = GLPISessionManager(**GLPI_DATA)
glpi_ticket = GLPITicketManager(glpi_session_manager)


ticket_data = {
        "login": "akimova_vi",
        # "login": "dyuzhev_mn",
        "name": "test_title",
        "content": 'test_description',
        "type": 1, # 1 для инцидента, 2 для запроса
        # "urgency": 3, # Срочность (1-5)
        # "impact": 3, # Влияние (1-5)
        # "priority": 3, # Приоритет (1-5)
        # "requesttypes_id": 14, # Источник запроса
        "itilcategories_id": 1, # ID Категории,
        # "_users_id_requester": 291, # ID пользователя-заявителя
        # "entities_id": 1  # ID организации (0 для корневой)
        # "organisation": "Проф ИТ"
    }


# Создаем заявку в GLPI
glpi_ticket.set_data(**ticket_data)
glpi_ticket.send_ticket()


