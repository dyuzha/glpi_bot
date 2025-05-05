from configparser import ConfigParser
from pathlib import Path
from os import environ


MAIL_CONFIG = environ.get('GLPI_TG_MAIL_CONFIGS') or \
    "mail_config.ini"

config = ConfigParser()
config.read(MAIL_CONFIG)
if not Path(MAIL_CONFIG).exists():
    raise FileNotFoundError(f"Config file {MAIL_CONFIG} not found")

MAIL_DATA = {
    'smtp_server' : config['data']['smtp_server'],
    'smtp_port' : config['data']['smtp_port'],
    'use_tls' : config['data']['use_tls'],
    'smtp_username' : config['data']['smtp_username'],
    'smtp_password' : config['data']['smtp_password']
}
