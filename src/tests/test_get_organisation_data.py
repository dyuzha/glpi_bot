from glpi_bot.glpi import GLPISessionManager, GLPIInterface
# from glpi_bot.services import GLPIIntte
from glpi_bot.config_handlers import GLPI_DATA


# Инициализация glpi
glpi_session_manager = GLPISessionManager(**GLPI_DATA)



# Создаем заявку в GLPI

with glpi_session_manager.get_session() as session:
    glpi_admins = GLPIInterface(session)
    data = glpi_admins.get_all_entities()
    print(data)
