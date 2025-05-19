from .db_service import DBInterface
from database import Database, SessionManager, Base

from .ad import get_user_mail
from .async_ad import AsyncLDAPService

from .mail_service import EmailConfirmation
from config_handlers import MAIL_DATA


db = Database('sqlite:////data/users.db')
db.create_tables(Base)
session_manager = SessionManager(db)
db_interface = DBInterface(session_manager)

mail_confirmation = EmailConfirmation(**MAIL_DATA)


