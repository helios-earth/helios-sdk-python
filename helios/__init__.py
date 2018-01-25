from helios.session.logger_setup import configure
from helios.session.token_manager import TokenManager

# Configure logger.
configure()

# Get authentication token and API URL.
AUTH_TOKEN, BASE_API_URL = TokenManager().start_session()

from . import core
from . import utilities
from .alerts import Alerts
from .cameras import Cameras
from .collections import Collections
from .observations import Observations

# Cleanup
del configure
del TokenManager

__version__ = '2.0.0'
