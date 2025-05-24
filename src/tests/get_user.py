from glpi_bot.glpi import GLPISessionManager, GLPIInterface
from glpi_bot.services import GLPIService
from glpi_bot.config_handlers import GLPI_DATA


# Инициализация glpi
glpi = GLPIInterface(**GLPI_DATA)
glpi_session_manager = GLPISessionManager(glpi)
glpi_service = GLPIService(glpi_session_manager)


login = "dyuzhev_mn"


# Получаем пользователя GLPI
with glpi_service.session_manager.get_session() as session:
    user = session.glpi.get_user(login)


print(user)
