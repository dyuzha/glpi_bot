import logging
import logging.config
import json
from pathlib import Path
from os import environ

LOG_CONF = environ.get('GLPI_TG_LOG_CONF') or \
    "logging_config.json"

def setup_logging():
    """Инициализация системы логирования"""
    try:
        with open(Path(LOG_CONF), 'r', encoding='utf-8') as f:
            logging_config = json.load(f)
    except FileNotFoundError:
        raise Exception(f"Файл конфигурации {LOG_CONF} не найден")
    except json.JSONDecodeError as e:
        raise Exception(f"Ошибка в JSON: {e.msg} (строка {e.lineno}, \
                столбец {e.colno})")

    # Если есть файловый обработчик, создаем папки и файл заранее
    if "handlers" in logging_config and "file" in logging_config["handlers"]:
        log_conf_path = Path(logging_config['handlers']['file']['filename'])
        log_conf_path.parent.mkdir(parents=True, exist_ok=True)  # Создаем папки
        if not log_conf_path.exists():
            log_conf_path.touch()

    # Применяем конфигурацию
    logging.config.dictConfig(logging_config)

    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")

    # Если определен файл, для создания логов: логируем это
    if log_conf_path:
        logger.debug(f"Log file initialized: {log_conf_path}")
    return logger
