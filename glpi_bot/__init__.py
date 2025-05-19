from database import Database, SessionManager, Base
from services import DBInterface
from config_handlers import DB


db = Database(DB['path'])
db.create_tables(Base)
session_manager = SessionManager(db)
db_interface = DBInterface(session_manager)
