from configparser import ConfigParser
from pathlib import Path
from os import environ


ORGS = environ.get('GLPI_TG_ORGNIZATIONS') or \
    "organizations.ini"

config = ConfigParser()
config.read(ORGS)
if not Path(ORGS).exists():
    raise FileNotFoundError(f"Config file {ORGS} not found")

ORGS_CONF = {
    'glpi_url': config['glpi']['glpi_url'],
    'app_token': config['glpi']['app_token'],
    'username': config['glpi']['username'],
    'password': config['glpi']['password']
}
TELEGRAM_TOKEN = config['telegram']['token']
