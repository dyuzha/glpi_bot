import logging
import logging.config
import json
from pathlib import Path
from os import environ

LOG_CONF = environ.get('GLPI_TG_LOG_CONF') or \
    "logging_config.json"

def setup_logging():
    """Инициализация системы логирования"""
    # Создаем папку для логов, если ее нет
    # LOG_DIR = os.environ.get('GLPI_TG_LOG_DIR') or Path("logs")
    # LOG_DIR.mkdir(exist_ok=True)

    try:
        with open(Path(LOG_CONF), 'r', encoding='utf-8') as f:
            logging_config = json.load(f)
    except FileNotFoundError:
        raise Exception(f"Файл конфигурации {LOG_CONF} не найден")
    except json.JSONDecodeError as e:
        raise Exception(f"Ошибка в JSON: {e.msg} (строка {e.lineno}, столбец {e.colno})")

    # Применяем конфигурацию
    logging.config.dictConfig(logging_config)

    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    return logger
