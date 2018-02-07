from . import core
from . import utilities
from .alerts_api import Alerts
from .cameras_api import Cameras
from .collections_api import Collections
from .observations_api import Observations
from .core.session import Session
# Configure logger.
from .utilities.logging_utils import configure_logger

configure_logger()

# Cleanup
del configure_logger

__version__ = '2.0.0'
