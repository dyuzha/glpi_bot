from glpi_bot.glpi.models import TicketBuilder
from glpi_bot.config_handlers import GLPI_DATA


ticket_data = {
        "login": "dyuzhev_mn",
        "name": "test_title",
        "content": 'test_description',
        "type": 1, # 1 для инцидента, 2 для запроса
        # "urgency": 3, # Срочность (1-5)
        # "impact": 3, # Влияние (1-5)
        # "priority": 3, # Приоритет (1-5)
        # "requesttypes_id": 14, # Источник запроса
        # "itilcategories_id": 1, ID Категории,
        # "_users_id_requester": 291, # ID пользователя-заявителя
        # "entities_id": 10  # ID организации (0 для корневой)
    }


# Создаем заявку в GLPI
with TicketBuilder(**GLPI_DATA) as glpi:
    result = glpi.create_ticket(**ticket_data)
    print(result)


