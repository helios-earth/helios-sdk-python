from helios.session.logger_setup import configure
from . import core
from . import utilities
from .alerts import Alerts
from .cameras import Cameras
from .collections import Collections
from .observations import Observations

# Configure logger.
configure()

# Cleanup
del configure

__version__ = '2.0.0'
