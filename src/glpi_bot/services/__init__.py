# configs
from glpi_bot.config_handlers import MAIL_DATA, GLPI_DATA

# # db
# from .db_service import DBService
# from glpi_bot.database import Database, Base, DBSessionManager

# # ad
# from .ad import get_user_mail
# from .async_ad import AsyncLDAPService
#
# # mail
# from .mail_service import EmailConfirmation

# glpi
from glpi_bot.glpi import GLPISessionManager, GLPIBase
from .glpi_service import GLPIService

# # Инициализация бд
# db = Database('sqlite:////data/users.db')
# db.create_tables(Base)
# db_session_manager = DBSessionManager(db)
# db_service = DBService(db_session_manager)
#
# # Инициализация mail
# mail_confirmation = EmailConfirmation(**MAIL_DATA)

# Инициализация glpi
glpi = GLPIBase(**GLPI_DATA)
glpi_session_manager = GLPISessionManager(glpi)
glpi_service = GLPIService(glpi_session_manager)
