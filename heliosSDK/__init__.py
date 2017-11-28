import json
import logging.config
import os

from heliosSDK.session.tokenManager import TokenManager

AUTH_TOKEN, BASE_API_URL = TokenManager().startSession()

from . import core
from . import utilities
from .alerts import Alerts
from .cameras import Cameras
from .collections import Collections
from .observations import Observations

__version__ = '1.1.1'

# Attempt to read SDK logging config file
_config_file = os.path.join(os.path.expanduser('~'), 'heliosSDK_logger_config.json')
_config = None
if os.path.exists(_config_file):
    try:
        with open(_config_file, 'r') as f:
            _config = json.load(f)
    except ValueError:
        _config = None

if _config is None:
    # Default logging configuration.    
    _log_file = os.path.join(os.path.expanduser('~'), 'heliosSDK.log')
    _config = {'version': 1, 'disable_existing_loggers': 1}

    _config['formatters'] = {}
    _config['formatters']['simple'] = {
        'format': '%(asctime)s-%(levelname)s-%(module)s-%(name)s-%(funcName)s: %(message)s', 'datefmt': '%H:%M:%S'}

    _config['handlers'] = {}
    _config['handlers']['console'] = {'class': 'logging.StreamHandler',
                                      'level': 'WARNING',
                                      'formatter': 'simple',
                                      'stream': 'ext://sys.stdout'}

    _config['root'] = {'level': 'INFO',
                       'handlers': ['console']}

    # Write default configuration to file
    try:
        with open(_config_file, 'w') as f:
            json.dump(_config, f)
    except IOError:
        pass

# Initialize logging
logging.config.dictConfig(_config)
logger = logging.getLogger(__name__)
