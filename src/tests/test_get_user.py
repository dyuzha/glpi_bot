from glpi_bot.glpi import GLPISessionManager, GLPIInterface
# from glpi_bot.services import GLPIService
from glpi_bot.config_handlers import GLPI_DATA

import logging

# Минимальная настройка логирования для всего приложения
def setup_logging():
    """Базовая конфигурация логирования в консоль"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# Инициализируем логирование
setup_logging()

# Получаем логгер для текущего модуля
logger = logging.getLogger(__name__)


# Инициализация glpi
glpi_session_manager = GLPISessionManager(**GLPI_DATA)

login = "dyuzhev_mn"
# login = "akimov_sv"

# Получаем пользователя GLPI
with glpi_session_manager.get_session() as session:
    glpi_interface = GLPIInterface(session)
    user = glpi_interface.get_user(login)
    print(user)
