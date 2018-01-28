from helios.session.logger_setup import configure
from helios.session.session_manager import SessionManager

# Configure logger.
configure()

# Get authentication token and API URL.
HELIOS_SESSION = SessionManager()
HELIOS_SESSION.start_session()
AUTH_TOKEN = HELIOS_SESSION.token
BASE_API_URL = HELIOS_SESSION.api_url

from . import core
from . import utilities
from .alerts import Alerts
from .cameras import Cameras
from .collections import Collections
from .observations import Observations

# Cleanup
del configure

__version__ = '2.0.0'
