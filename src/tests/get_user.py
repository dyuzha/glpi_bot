from glpi_bot.glpi import GLPISessionManager, GLPIInterface
# from glpi_bot.services import GLPIService
from glpi_bot.config_handlers import GLPI_DATA


# Инициализация glpi
glpi_session_manager = GLPISessionManager(**GLPI_DATA)

login = "dyuzhev_mn"

# Получаем пользователя GLPI
with glpi_session_manager.get_session() as session:
    glpi_interface = GLPIInterface(session)

print()
