from configparser import ConfigParser
from pathlib import Path
from os import environ


CONFIG_DIR = environ.get('GLPI_TG_CONFIG_DIR', '/configs')
MAIL_CONF_FILE = environ.get('GLPI_TG_MAIL_CONFIG', 'mail_config.ini')
MAIL_CONF = str(Path(CONFIG_DIR) / MAIL_CONF_FILE)


config = ConfigParser()
config.read(MAIL_CONF)
if not Path(MAIL_CONF).exists():
    raise FileNotFoundError(f"Config file {MAIL_CONF} not found")


MAIL_DATA = {
    'smtp_server' : config['data']['smtp_server'],
    'smtp_port' : config['data']['smtp_port'],
    'use_tls': config.getboolean('data', 'use_tls'),  # Преобразует строку в bool
    'smtp_username' : config['data']['smtp_username'],
    'smtp_password' : config['data']['smtp_password']
}
