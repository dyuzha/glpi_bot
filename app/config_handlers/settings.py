from configparser import ConfigParser
from pathlib import Path
from os import environ


SETTINGS = environ.get('GLPI_TG_SETTINGS_CONF') or \
    "settings.ini"

config = ConfigParser()
config.read(SETTINGS)
if not Path(SETTINGS).exists():
    raise FileNotFoundError(f"Config file {SETTINGS} not found")

GLPI_CONFIG = {
    'glpi_url': config['glpi']['glpi_url'],
    'app_token': config['glpi']['app_token'],
    'username': config['glpi']['username'],
    'password': config['glpi']['password']
}
TELEGRAM_TOKEN = config['telegram']['token']
