from configparser import ConfigParser
from pathlib import Path
from os import environ


CONFIG_DIR = environ.get('GLPI_TG_CONFIG_DIR', '/configs')
SETTINGS_FILE = environ.get('GLPI_TG_SETTINGS', 'settings.ini')
SETTINGS = str(Path(CONFIG_DIR) / SETTINGS_FILE)


config = ConfigParser()
config.read(SETTINGS)
if not Path(SETTINGS).exists():
    raise FileNotFoundError(f"Config file {SETTINGS} not found")


GLPI_DATA = {
    'glpi_url': config['glpi']['glpi_url'],
    'app_token': config['glpi']['app_token'],
    'username': config['glpi']['username'],
    'password': config['glpi']['password']
}
TELEGRAM_TOKEN = config['telegram']['token']
