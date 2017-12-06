import json
import logging.config
import os

from heliosSDK.session.token_manager import TokenManager

AUTH_TOKEN, BASE_API_URL = TokenManager().start_session()

from . import core
from . import utilities
from .alerts import Alerts
from .cameras import Cameras
from .collections import Collections
from .observations import Observations

__version__ = '1.1.1'

# Attempt to read SDK logging config file
CONFIG_FILE = os.path.join(os.path.expanduser('~'),
                           'heliosSDK_logger_config.json')
CONFIG = None
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r') as f:
            CONFIG = json.load(f)
    except ValueError:
        CONFIG = None

if CONFIG is None:
    # Default logging configuration.
    CONFIG = {'version': 1, 'disable_existing_loggers': 1}

    CONFIG['formatters'] = {}
    CONFIG['formatters']['simple'] = {'format': '%(asctime)s-%(levelname)s'
                                                '-%(module)s-%(name)s'
                                                '-%(funcName)s: %(message)s',
                                      'datefmt': '%H:%M:%S'}

    CONFIG['handlers'] = {}
    CONFIG['handlers']['console'] = {'class': 'logging.StreamHandler',
                                     'level': 'WARNING',
                                     'formatter': 'simple',
                                     'stream': 'ext://sys.stdout'}

    CONFIG['root'] = {'level': 'INFO',
                      'handlers': ['console']}

    # Write default configuration to file
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(CONFIG, f)
    except IOError:
        pass

# Initialize logging
logging.config.dictConfig(CONFIG)

# Cleanup unused constants
del CONFIG
del CONFIG_FILE
