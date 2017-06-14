from heliosSDK.session.tokenManager import TokenManager
AUTH_TOKEN, BASE_API_URL = TokenManager().startSession()

from . import core
from . import utilities
from .alerts import Alerts
from .cameras import Cameras
from .collections import Collections
from .observations import Observations

__version__ = '0.1.3'