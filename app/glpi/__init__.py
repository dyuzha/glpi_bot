# glpi/__init__.py
from .api import GLPIConnection, GLPIService  # Экспорт класса для удобного импорта

__all__ = ['GLPIConnection', 'GLPIService']  # Какие объекты будут доступны при from glpi import *

