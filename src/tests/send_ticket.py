from glpi_bot.glpi.session import GLPISessionManager, GLPIBase
from glpi_bot.services import GLPIService
from glpi_bot.config_handlers import GLPI_DATA


# Инициализация glpi
glpi = GLPIBase(**GLPI_DATA)
glpi_session_manager = GLPISessionManager(glpi)
glpi_service = GLPIService(glpi_session_manager)


ticket_data = {
        "login": "akimova_vi",
        "name": "test_title",
        "content": 'test_description',
        "type": 1, # 1 для инцидента, 2 для запроса
        # "urgency": 3, # Срочность (1-5)
        # "impact": 3, # Влияние (1-5)
        # "priority": 3, # Приоритет (1-5)
        # "requesttypes_id": 14, # Источник запроса
        # "itilcategories_id": 1, # ID Категории,
        # "_users_id_requester": 291, # ID пользователя-заявителя
        "entities_id": 1  # ID организации (0 для корневой)
    }


# Создаем заявку в GLPI
glpi_service.create_ticket(**ticket_data)
