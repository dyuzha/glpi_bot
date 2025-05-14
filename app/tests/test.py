from config_handlers import *
from glpi import GLPIConnection, GLPIService
ticket_data = {
    "input": {
        "name": 'title',
        "content": 'description',
        "type": 1, # 1 для инцидента, 2 для запроса
        # "urgency": 3, # Срочность (1-5)
        # "impact": 3, # Влияние (1-5)
        # "priority": 3, # Приоритет (1-5)
        "requesttypes_id": 1, # Источник запроса
        # 8 - Ничего
        # 7 - Formcreator
        # 6 - other
        # 5 - written
        # 4 - direct
        # 3 - телефон
        # 2 - email
        # 1 - helpdesk
        # 0 - Ничего
        # "itilcategories_id": 1, ID Категории,
        "_users_id_requester": 291, # ID пользователя-заявителя
        "entities_id": 10  # ID организации (0 для корневой)
    }
}

with GLPIConnection(**GLPI_CONFIG) as glpi:
    response = glpi._make_request("GET", "RequestType")
    print("Доступные типы запросов:", response)
