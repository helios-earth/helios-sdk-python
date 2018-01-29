from . import core
from . import utilities
from .alerts import Alerts
from .cameras import Cameras
from .collections import Collections
from .observations import Observations
from helios.core.session import Session
# Configure logger.
from .utilities.logging_utils import configure_logger

configure_logger()

# Cleanup
del configure_logger

__version__ = '2.0.0'
