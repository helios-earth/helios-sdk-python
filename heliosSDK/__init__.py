from heliosSDK.session.tokenManager import TokenManager
AUTH_TOKEN, BASE_API_URL = TokenManager().startSession()

import os
import logging
import logging.config

from . import core
from . import utilities
from .alerts import Alerts
from .cameras import Cameras
from .collections import Collections
from .observations import Observations

__version__ = '0.1.3'

# If applicable, delete the existing log file to generate a fresh log file
if os.path.isfile("heliosSDK.log"):
    os.remove("heliosSDK.log")
 
# Create the Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
 
# Create the Handler for logging data to a file
logger_handler = logging.FileHandler('heliosSDK.log')
logger_handler.setLevel(logging.DEBUG)
 
# Create a Formatter for formatting the log messages
logger_formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(module)s-%(name)s-%(funcName)s: %(message)s',
                                     '%H:%M:%S')
 
# Add the Formatter to the Handler
logger_handler.setFormatter(logger_formatter)
 
# Add the Handler to the Logger
logger.addHandler(logger_handler)
logger.info('Successfully configured logger()!')