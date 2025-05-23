from glpi_bot.glpi.session import GLPISessionManager, GLPIBase
from glpi_bot.services import GLPIService
from glpi_bot.config_handlers import GLPI_DATA


# Инициализация glpi
glpi = GLPIBase(**GLPI_DATA)
glpi_session_manager = GLPISessionManager(glpi)
glpi_service = GLPIService(glpi_session_manager)


login = "dyuzhev_mn"


# Получаем пользователя GLPI
result = glpi_service.get_user("akimova_vi")
print(result)
