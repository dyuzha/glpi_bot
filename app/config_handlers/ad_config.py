from configparser import ConfigParser
from pathlib import Path
from os import environ


AD_CONFIGS = environ.get('GLPI_TG_AD_CONFIGS') or \
    "ad_configs.ini"

config = ConfigParser()
config.read(AD_CONFIGS)
if not Path(AD_CONFIGS).exists():
    raise FileNotFoundError(f"Config file {AD_CONFIGS} not found")

AD_CONFIG = {
    'server': config['ad']['server'],
    'user': config['ad']['user'],
    'password': config['ad']['password']
}
